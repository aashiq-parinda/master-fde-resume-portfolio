import json
import asyncio
import redis.asyncio as redis
from typing import Callable, Awaitable, Optional

from src.config import settings
from src.utils.logger import get_logger, telemetry

logger = get_logger("streaming")

class RedisStreamManager:
    """
    Manages connections and operations to Redis Pub/Sub.
    Acts as the lightweight, asynchronous event-streaming layer.
    """
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.channel_name = "factory:sensor_readings"

    async def connect(self):
        if not self.client:
            logger.info(f"Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}...")
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )

    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Redis client connection closed.")

    async def publish_reading(self, reading: dict) -> int:
        """Publishes a sensor reading payload to the message stream."""
        if not self.client:
            await self.connect()
        
        try:
            payload = json.dumps(reading)
            # Returns the number of subscribers that received the message
            receivers = await self.client.publish(self.channel_name, payload)
            return receivers
        except Exception as e:
            logger.error(f"Failed to publish message to Redis: {e}")
            telemetry.record_error()
            return 0

    async def start_consumer(self, callback: Callable[[dict], Awaitable[None]], stop_event: asyncio.Event):
        """
        Subscribes to the sensor reading channel and processes incoming messages.
        Runs until the stop_event is set.
        """
        if not self.client:
            await self.connect()

        pubsub = self.client.pubsub()
        await pubsub.subscribe(self.channel_name)
        logger.info(f"Subscribed to Redis channel: {self.channel_name}. Consumer active.")

        try:
            while not stop_event.is_set():
                try:
                    # Non-blocking check for message
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message and message["type"] == "message":
                        data = json.loads(message["data"])
                        # Handle the message using the callback
                        await callback(data)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error consuming message from channel: {e}")
                    telemetry.record_error()
                    await asyncio.sleep(1.0) # Backoff
        finally:
            await pubsub.unsubscribe(self.channel_name)
            await pubsub.close()
            logger.info("Redis Pub/Sub consumer stopped.")

stream_manager = RedisStreamManager()
