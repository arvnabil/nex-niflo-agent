import json
import logging
from typing import Dict, Any
from skills.registry import registry
from agents.registry import agent_registry # 🚀 The real source of truth

logger = logging.getLogger("nex-v2-tools")

class ToolManager:
    """Standardized tool wrapper for Nex V2 Orchestrator."""
    
    def __init__(self):
        self.registry = registry

    def get_descriptions(self) -> str:
        """Returns string descriptions of all available tools for the agent prompt."""
        desc = self.registry.get_skill_descriptions()
        # ⚡ Add system-level tools
        desc += "- list_agents: Get the list of all active agents in Nex Squad.\n"
        return desc

    async def execute(self, skill_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a tool and ensures a uniform JSON response."""
        logger.info(f"[TOOLS-V2] Executing: {skill_id} with params: {params}")
        
        try:
            # 🚀 SYSTEM TOOL: list_agents
            if skill_id == "list_agents":
                agents = agent_registry.list_agents()
                names = [a['name'] for a in agents]
                return {
                    "status": "success",
                    "message": "List agen berhasil ditarik.",
                    "data": {"agents": names}
                }

            # Standardizing parameters
            clean_params = {k: v for k, v in params.items() if k not in ["session_id"]}
            
            # Call the existing registry
            result = await registry.execute(skill_id, **clean_params)
            
            # Normalize result structure
            if isinstance(result, dict) and "status" in result:
                return result
                
            return {
                "status": "success",
                "message": str(result),
                "data": {"raw_output": result}
            }
            
        except Exception as e:
            logger.error(f"[TOOLS-V2] Tool failure ({skill_id}): {str(e)}")
            return {
                "status": "error",
                "message": f"Execution failed: {str(e)}",
                "data": {}
            }
