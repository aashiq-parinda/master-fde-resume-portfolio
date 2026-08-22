import os
import csv
import xml.etree.ElementTree as ET
import asyncio
import logging
from typing import Dict, Any, List
import httpx
from src.config import settings
from src.database import db_manager
from src.engine.mapping import map_rest_payload, map_xml_element, map_csv_row
from src.engine.retry import execute_with_retry, route_to_dlq

logger = logging.getLogger("scheduler")

class IngestionEngine:
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self.running = False
        self.http_client: Optional[httpx.AsyncClient] = None

    async def start(self):
        """Starts the periodic background ingestion loops."""
        if self.running:
            return
        
        self.running = True
        self.http_client = httpx.AsyncClient(timeout=10.0)
        
        # Resolve drop directory
        os.makedirs(settings.CSV_DROP_DIR, exist_ok=True)
        
        # Fetch active sources from registry
        sources = await db_manager.fetch("SELECT id, sync_interval, type FROM sources WHERE is_active = TRUE")
        
        for src in sources:
            source_id = src["id"]
            interval = src["sync_interval"]
            source_type = src["type"]
            
            # Webhooks are push-based, so we don't start a polling loop for them
            if source_type == "webhook":
                logger.info(f"Ingestion source [{source_id}] (webhook) ready. Awaiting events.")
                continue
                
            task = asyncio.create_task(self._poll_loop(source_id, interval, source_type))
            self.tasks.append(task)
            logger.info(f"Started polling loop for [{source_id}] (interval: {interval}s)")

    async def stop(self):
        """Stops the ingestion engine background tasks."""
        self.running = False
        
        for task in self.tasks:
            task.cancel()
            
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks = []
            
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
            
        logger.info("Ingestion engine loops stopped successfully.")

    async def _poll_loop(self, source_id: str, interval: int, source_type: str):
        """Generic infinite polling loop for a specific legacy source."""
        # Wait a small staggered duration to prevent start surges
        await asyncio.sleep(interval * 0.1)
        
        while self.running:
            logger.debug(f"Triggering sync for [{source_id}]...")
            try:
                if source_type == "rest":
                    await self._sync_rest(source_id)
                elif source_type == "xml":
                    await self._sync_xml(source_id)
                elif source_type == "csv":
                    await self._sync_csv(source_id)
            except Exception as e:
                logger.error(f"Sync loop execution error on source [{source_id}]: {e}")
                
            await asyncio.sleep(interval)

    async def _sync_rest(self, source_id: str):
        """Fetches from REST endpoint, maps, and upserts data."""
        async def fetch_action():
            headers = {"Authorization": f"Bearer {settings.REST_SOURCE_API_KEY}"}
            # Retrieve REST source endpoint URL
            url = await db_manager.fetchval("SELECT endpoint FROM sources WHERE id = $1", source_id)
            
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

        try:
            customers = await execute_with_retry(source_id, fetch_action)
            for cust in customers:
                try:
                    mapped = map_rest_payload(cust)
                    await self._upsert_record(source_id, mapped)
                except Exception as map_err:
                    await route_to_dlq(source_id, str(cust), f"REST Mapping failed: {map_err}")
        except Exception as conn_err:
            logger.error(f"REST Ingest Connection failed: {conn_err}")

    async def _sync_xml(self, source_id: str):
        """Fetches XML records, parses elements, maps, and upserts."""
        async def fetch_action():
            auth = (settings.XML_SOURCE_USERNAME, settings.XML_SOURCE_PASSWORD)
            url = await db_manager.fetchval("SELECT endpoint FROM sources WHERE id = $1", source_id)
            
            response = await self.http_client.get(url, auth=auth)
            response.raise_for_status()
            return response.text

        try:
            xml_text = await execute_with_retry(source_id, fetch_action)
            try:
                root = ET.fromstring(xml_text)
                for element in root.findall("account"):
                    try:
                        mapped = map_xml_element(element)
                        await self._upsert_record(source_id, mapped)
                    except Exception as map_err:
                        raw_str = ET.tostring(element, encoding="unicode")
                        await route_to_dlq(source_id, raw_str, f"XML Mapping failed: {map_err}")
            except Exception as parse_err:
                await route_to_dlq(source_id, xml_text[:1000], f"XML Parse failure: {parse_err}")
        except Exception as conn_err:
            logger.error(f"XML Ingest Connection failed: {conn_err}")

    async def _sync_csv(self, source_id: str):
        """Scans local folder, processes CSV files, maps rows, and deletes files."""
        # Wrap folder scan in retry logic
        async def scan_action():
            folder = await db_manager.fetchval("SELECT endpoint FROM sources WHERE id = $1", source_id)
            if not os.path.exists(folder):
                return []
            return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".csv")]

        try:
            csv_files = await execute_with_retry(source_id, scan_action)
            for filepath in csv_files:
                logger.info(f"Processing CSV file: {filepath}")
                try:
                    with open(filepath, mode="r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                mapped = map_csv_row(row)
                                await self._upsert_record(source_id, mapped)
                            except Exception as row_err:
                                await route_to_dlq(source_id, str(row), f"CSV Row Mapping failed: {row_err}")
                    # Delete file after successful processing
                    os.remove(filepath)
                    logger.info(f"Deleted processed CSV file: {filepath}")
                except Exception as file_err:
                    logger.error(f"Error processing CSV file [{filepath}]: {file_err}")
                    await route_to_dlq(source_id, filepath, f"CSV File processing failure: {file_err}")
        except Exception as scan_err:
            logger.error(f"CSV Directory scan failed: {scan_err}")

    async def _upsert_record(self, source_id: str, record: Dict[str, Any]):
        """Upserts a mapped record into the central database."""
        await db_manager.execute("""
            INSERT INTO records (source_id, external_id, name, email, balance, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (source_id, external_id) 
            DO UPDATE SET 
                name = EXCLUDED.name,
                email = EXCLUDED.email,
                balance = EXCLUDED.balance,
                status = EXCLUDED.status,
                synced_at = CURRENT_TIMESTAMP
        """, source_id, record["external_id"], record["name"], record["email"], record["balance"], record["status"])

# Singleton engine instance
ingestion_engine = IngestionEngine()
