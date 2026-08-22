import asyncio
import random
import logging
from typing import Callable, Any
from src.database import db_manager

logger = logging.getLogger("retry")

async def route_to_dlq(source_id: str, raw_payload: str, error_message: str):
    """Saves malformed payloads and mapping errors into the database DLQ table."""
    logger.error(f"DLQ INGESTION for [{source_id}]: {error_message}")
    try:
        await db_manager.execute("""
            INSERT INTO dead_letter_queue (source_id, raw_payload, error_message)
            VALUES ($1, $2, $3)
        """, source_id, raw_payload, error_message)
    except Exception as e:
        logger.critical(f"CRITICAL: Failed to write payload to Dead Letter Queue database table: {e}")

async def log_health_metric(source_id: str, status: str, latency_ms: float, success: bool):
    """Saves health metrics and updates ingestion observability records."""
    success_inc = 1 if success else 0
    error_inc = 0 if success else 1
    
    try:
        # Save historical log
        await db_manager.execute("""
            INSERT INTO health_metrics (source_id, status, latency_ms, success_count, error_count)
            VALUES ($1, $2, $3, $4, $5)
        """, source_id, status, latency_ms, success_inc, error_inc)
        
        # Update last sync timestamp on sources registry
        await db_manager.execute("""
            UPDATE sources 
            SET last_sync = CURRENT_TIMESTAMP
            WHERE id = $1
        """, source_id)
    except Exception as e:
        logger.error(f"Failed to log health metric for source {source_id}: {e}")

async def execute_with_retry(
    source_id: str, 
    action_fn: Callable[..., Any], 
    *args, 
    max_retries: int = 3, 
    base_delay: float = 1.5,
    **kwargs
) -> Any:
    """
    Executes a network or extraction task with exponential backoff and jitter.
    If all retries fail, it logs a degraded/down status and raises the exception.
    """
    retries = 0
    while True:
        try:
            start_time = asyncio.get_event_loop().time()
            result = await action_fn(*args, **kwargs)
            end_time = asyncio.get_event_loop().time()
            
            # Log successful health check
            latency = (end_time - start_time) * 1000.0
            await log_health_metric(source_id, "healthy", latency, success=True)
            return result
        except Exception as e:
            retries += 1
            if retries > max_retries:
                logger.error(f"Action failed on source [{source_id}] after {max_retries} attempts. Raising error.")
                # Mark as degraded/down
                await log_health_metric(source_id, "down", 0.0, success=False)
                raise e
            
            # Exponential Backoff with Jitter
            delay = (base_delay * (2 ** (retries - 1))) + random.uniform(0.1, 0.5)
            logger.warning(
                f"Attempt {retries} failed for [{source_id}] due to error: {e}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            # Log degraded state temporarily
            await log_health_metric(source_id, "degraded", 0.0, success=False)
            await asyncio.sleep(delay)
