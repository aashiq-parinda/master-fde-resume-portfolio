import asyncio
import logging
import asyncpg
from src.config import settings

logger = logging.getLogger("database")

DB_SCHEMA = """
-- 1. Integration Sources Registry
CREATE TABLE IF NOT EXISTS sources (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'rest', 'xml', 'csv', 'webhook'
    auth_type VARCHAR(20) NOT NULL, -- 'api_key', 'basic', 'none', 'signature'
    endpoint TEXT NOT NULL,
    sync_interval INTEGER DEFAULT 30, -- in seconds
    is_active BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP WITH TIME ZONE
);

-- 2. Unified Customer Records
CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(50) REFERENCES sources(id) ON DELETE CASCADE,
    external_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(254) NOT NULL,
    balance NUMERIC(15, 2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'active',
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_id, external_id)
);

-- 3. Dead Letter Queue for Ingestion Failures
CREATE TABLE IF NOT EXISTS dead_letter_queue (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(50) REFERENCES sources(id) ON DELETE CASCADE,
    raw_payload TEXT NOT NULL,
    error_message TEXT NOT NULL,
    failed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Ingestion Health & Observability Metrics
CREATE TABLE IF NOT EXISTS health_metrics (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(50) REFERENCES sources(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL, -- 'healthy', 'degraded', 'down'
    latency_ms FLOAT DEFAULT 0.0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

# Default seed data for our 4 legacy sources
SEED_SOURCES = [
    ("legacy_rest", "Legacy CRM REST API", "rest", "api_key", "http://127.0.0.1:8001/mock/rest/customers", 15, True),
    ("legacy_soap", "Legacy billing SOAP/XML API", "xml", "basic", "http://127.0.0.1:8001/mock/xml/accounts", 20, True),
    ("legacy_csv", "Legacy mainframe CSV file drop", "csv", "none", "./csv_drop", 10, True),
    ("legacy_webhook", "Legacy order webhook stream", "webhook", "signature", "http://127.0.0.1:8001/api/webhook", 0, True)
]

class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Start the asyncpg pool."""
        if self.pool is not None:
            return
        
        logger.info(f"Connecting to database at {settings.DB_HOST}:{settings.DB_PORT}...")
        try:
            self.pool = await asyncpg.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                min_size=2,
                max_size=10
            )
            logger.info("Database connection pool established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise e

    async def initialize_database(self):
        """Create tables and insert seed data."""
        await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                logger.info("Executing database schema initialization...")
                await conn.execute(DB_SCHEMA)
                
                # Seed sources
                for source_id, name, type_, auth_type, endpoint, interval, is_active in SEED_SOURCES:
                    await conn.execute("""
                        INSERT INTO sources (id, name, type, auth_type, endpoint, sync_interval, is_active)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (id) DO UPDATE 
                        SET name = EXCLUDED.name, 
                            type = EXCLUDED.type, 
                            auth_type = EXCLUDED.auth_type,
                            endpoint = EXCLUDED.endpoint, 
                            sync_interval = EXCLUDED.sync_interval;
                    """, source_id, name, type_, auth_type, endpoint, interval, is_active)
                    
                logger.info("Database schema and seed records successfully initialized.")

    async def execute(self, query: str, *args):
        """Execute a write/update statement."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Fetch a single scalar value."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed.")

db_manager = DatabaseManager()
