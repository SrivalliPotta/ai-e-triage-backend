import json
import os

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


class RedisEventBus:
    def __init__(self, url: str | None = None):
        # Always keep fallback memory storage
        self._events = []

        # Redis package not installed
        if redis is None:
            self.url = None
            self.client = None
            print("[EVENT BUS] Redis package not installed. Using memory fallback.")
            return

        # Redis installed
        self.url = url or os.getenv(
            "REDIS_URL",
            "redis://127.0.0.1:6379/0"
        )

        self.client = redis.from_url(
            self.url,
            decode_responses=True
        )

    async def publish(self, channel: str, event: dict):
        payload = json.dumps(event)

        # Redis unavailable
        if self.client is None:
            self._events.append(
                {
                    "channel": channel,
                    "payload": payload
                }
            )

            print(f"[MEMORY EVENT] {channel} -> {event}")
            return

        # Try Redis publish
        try:
            await self.client.publish(channel, payload)

            print(f"[REDIS EVENT] {channel} -> {event}")

        except Exception as e:
            # Redis server offline
            print(f"[REDIS ERROR] {e}")

            # Fallback memory event
            self._events.append(
                {
                    "channel": channel,
                    "payload": payload
                }
            )

            print(f"[FALLBACK EVENT] {channel} -> {event}")

    async def close(self):
        if self.client is None:
            return

        await self.client.close()