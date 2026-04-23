import logging
import time
from functools import wraps

# Technical Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/app/core/agent.log")
    ]
)

class NexObservability:
    def __init__(self):
        self.logger = logging.getLogger("nex-obs")

    def track_latency(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start
            self.logger.info(f"[METRIC] {func.__name__} took {duration:.4f}s")
            return result
        return wrapper

    def log_intent(self, session_id, user_input, intent):
        self.logger.info(f"[INTENT] Session: {session_id} | Input: {user_input[:50]}... | Intent: {intent}")

    def log_skill(self, session_id, skill_name, params):
        self.logger.info(f"[SKILL] Session: {session_id} | Executing: {skill_name} | Params: {params}")

    def log_rag(self, session_id, hits, score=None):
        status = "HIT" if hits > 0 else "MISS"
        self.logger.info(f"[RAG] Session: {session_id} | Result: {status} | Hits: {hits} | Best Score: {score}")

# Singleton
observability = NexObservability()
