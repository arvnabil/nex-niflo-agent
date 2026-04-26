import logging
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from .supervisor import NexSupervisor
from .agent import NexAgent
from .executor import MissionExecutor
from .tools import ToolManager
from agents.registry import agent_registry

logger = logging.getLogger("nex-v2-orchestrator")

# 🔥 In-memory session state for V3.3
# In production, this can be moved to Redis or SQLite
SESSION_STATE: Dict[str, Dict[str, Any]] = {}

class NexOrchestrator:
    """The Master Orchestrator V3.3: Managing Multi-Turn Interaction."""
    
    def __init__(self):
        self.supervisor = NexSupervisor()
        self.tools = ToolManager()

    async def execute_stream(self, user_input: str, history: str = "", session_id: str = "default") -> AsyncGenerator[str, None]:
        """Orchestrates mission with persistent state for V3.3 Clarification."""
        logger.info(f"[ORCH-V3.3] Streaming mission for session: {session_id}")
        
        # 1. RETRIEVE OR INITIALIZE SESSION STATE
        if session_id not in SESSION_STATE:
            SESSION_STATE[session_id] = {"pending_clarification": None}
        
        state = SESSION_STATE[session_id]
        
        # 2. HANDLE PENDING CLARIFICATION (V3.3 PRIORITY)
        if state.get("pending_clarification"):
            logger.info(f"[ORCH-V3.3] Session {session_id} has pending clarification. Resolving...")
            # Route back to Scheduler manually to handle the response
            agent_data = agent_registry.get_agent("scheduler")
            agent = NexAgent("scheduler", agent_data["description"])
            executor = MissionExecutor(agent, self.tools)
            
            async for chunk in executor.run_mission_stream(user_input, history, state):
                yield chunk
            return

        # 3. NORMAL ROUTING (If no pending state)
        routing_result = await self.supervisor.route(user_input, history)
        
        # Immediate Response (Conversational)
        if routing_result["routing"]["intent"] == "conversational":
            yield routing_result["routing"]["soft_confirmation"]
            return

        # Explicit Confirmation Message
        yield f"{routing_result['routing']['soft_confirmation']}\n"
        await asyncio.sleep(0.5)

        # Plan Execution
        for task_info in routing_result["plan"]:
            agent_data = agent_registry.get_agent(task_info["agent"])
            agent = NexAgent(task_info["agent"], agent_data["description"])
            executor = MissionExecutor(agent, self.tools)
            
            # Pass the session state to the executor
            async for chunk in executor.run_mission_stream(task_info["task"], history, state):
                yield chunk

    def clear_session(self, session_id: str):
        """Clears the session memory."""
        if session_id in SESSION_STATE:
            del SESSION_STATE[session_id]
            logger.info(f"[ORCH-V3.3] Session {session_id} cleared.")
