import logging
from core.v2.orchestrator import NexOrchestrator

logger = logging.getLogger("nex-sovereign")

class SovereignSupervisor:
    """
    V3.3 Sequential Bridge.
    Synchronized with NexOrchestrator V3.3 Interactive Mode.
    """
    def __init__(self):
        self.orchestrator = NexOrchestrator()

    async def process_request(self, session_id: str, user_input: str, history: str = "", channel: str = "web"):
        """
        Flow-based processing synchronized with Orchestrator V3.3.
        """
        logger.info(f"[SOVEREIGN-V3.3] Directing request to Orchestrator V3.3 flow.")
        
        try:
            # 🔥 V3.3 SYNC: Orchestrator handles routing, intros, and clarifying states internally
            async for chunk in self.orchestrator.execute_stream(user_input, history, session_id):
                # The speaker/role is handled by the orchestrator/executor
                # For backward compatibility with gateway/main.py, we yield a tuple
                # We can detect agent_id from the context if needed, but 'sovereign' is safe for streaming
                yield ("sovereign", chunk)
            
        except Exception as e:
            logger.error(f"[SOVEREIGN-V3.3] Fatal Error: {e}")
            import traceback
            traceback.print_exc()
            yield ("sovereign", f"🚨 **Error Fatal:** `{str(e)}` \n\nSistem gue lagi glitch, coba lagi pas sinyal stabil ya Bro!")

# Singleton
sovereign = SovereignSupervisor()
