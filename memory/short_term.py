import redis
import json
import os
import logging

logger = logging.getLogger("nex-memory")

class RedisStore:
    """
    Hybrid Memory Store for Nex Agent Platform.
    Supports Global Shared Memory and Isolated Agent Memory.
    """
    def __init__(self, host=None, port=6379):
        self.host = host or os.getenv("REDIS_HOST", "nex-niflo-agent-redis")
        try:
            self.client = redis.Redis(host=self.host, port=port, decode_responses=True)
            self.client.ping()
        except Exception as e:
            logger.error(f"[MEMORY] Redis connection failed: {e}")
            self.client = None

    def save(self, session_id: str, messages: list, segment: str = "global", expiry: int = 3600):
        """Saves messages to a specific memory segment (global, analyst, sales, etc.)"""
        if not self.client: return False
        key = f"session:{session_id}:{segment}"
        try:
            self.client.set(key, json.dumps(messages), ex=expiry)
            return True
        except Exception as e:
            logger.error(f"[MEMORY] Save failed for {key}: {e}")
            return False

    def get(self, session_id: str, segment: str = "global") -> list:
        """Retrieves messages from a specific memory segment."""
        if not self.client: return []
        key = f"session:{session_id}:{segment}"
        try:
            data = self.client.get(key)
            return json.loads(data) if data else []
        except Exception as e:
            logger.error(f"[MEMORY] Get failed for {key}: {e}")
            return []

    def get_all_segments(self, session_id: str) -> dict:
        """Helper to get a snapshot of all memory for a session (excluding isolated thoughts)"""
        if not self.client: return {}
        # We usually only want global + visible results
        return {
            "global": self.get(session_id, "global"),
            "results": self.get(session_id, "results")
        }

    def clear_session(self, session_id: str):
        if not self.client: return
        keys = self.client.keys(f"session:{session_id}:*")
        if keys:
            self.client.delete(*keys)

# Singleton instance
memory_store = RedisStore()
