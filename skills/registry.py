import logging
from typing import Dict, Any

# Import all skills
from skills.productivity.task_reminder import task_reminder
from skills.productivity.summarize import summarize
from skills.knowledge.rag_search import rag_search
from skills.knowledge.tavily_search import tavily_search
from skills.knowledge.weather_check import weather_check
from skills.automation.n8n_workflow import n8n_workflow
from skills.automation.zoom_engineer import zoom_engineer
from skills.automation.activ_api import activ_api
from skills.automation.github_specialist import github_specialist
from skills.automation.calendar_specialist import calendar_list, calendar_create
from skills.automation.zcalendar_hybrid import zcalendar_create
from skills.agent_tools.browser import browser_agent
from skills.agent_tools.elevenlabs import elevenlabs_tts
from skills.agent_tools.niflows import niflows
from skills.agent_tools.identity import get_linking_code, resolve_linking_code

logger = logging.getLogger("nex-skills")

class SkillRegistry:
    def __init__(self):
        # The new hierarchical skills dictionary
        self.SKILLS: Dict[str, Any] = {
            "summarize": {
                "fn": summarize,
                "description": "Summarize long text into key insights",
                "type": "productivity",
                "params": {"text": "string"}
            },
            "task_reminder": {
                "fn": task_reminder,
                "description": "Create reminder or schedule task",
                "type": "productivity",
                "params": {"task": "string", "time": "string (optional)"}
            },
            "rag_search": {
                "fn": rag_search,
                "description": "Search internal knowledge base (RAG)",
                "type": "knowledge",
                "params": {"query": "string"}
            },
            "web_search": {
                "fn": tavily_search,
                "description": "Search the internet for real-time information",
                "type": "knowledge",
                "params": {"query": "string"}
            },
            "weather_check": {
                "fn": weather_check,
                "description": "Check current weather and temperature for a city",
                "type": "knowledge",
                "params": {"city": "string"}
            },
            "n8n_workflow": {
                "fn": n8n_workflow,
                "description": "Trigger automation workflow via webhook",
                "type": "automation",
                "params": {"webhook": "url"}
            },
            "zoom_engineer": {
                "fn": zoom_engineer,
                "description": "Schedule Zoom meeting via n8n automation",
                "type": "automation",
                "params": {"topic": "string", "datetime_iso": "string", "host_email": "string (optional)"}
            },
            "github": {
                "fn": github_specialist,
                "description": "Interact with GitHub (repos, issues, stars)",
                "type": "automation",
                "params": {"action": "string", "repo": "string (optional)"}
            },
            "calendar_list": {
                "fn": calendar_list,
                "description": "Cek daftar agenda di Google Calendar",
                "type": "automation",
                "params": {"start_time": "string (optional)", "end_time": "string (optional)"}
            },
            "calendar_create": {
                "fn": calendar_create,
                "description": "Buat agenda baru di Google Calendar",
                "type": "automation",
                "params": {"topic": "string", "description": "string (optional)", "start_time": "string", "end_time": "string (optional)"}
            },
            "zcalendar_create": {
                "fn": zcalendar_create,
                "description": "Super-Skill: Buat ZOOM + KALENDER sekaligus (Gunakan ini untuk permintaan Meeting)",
                "type": "automation",
                "params": {"topic": "string", "start_time": "string", "host_email": "string (optional)"}
            },
            "activ_api": {
                "fn": activ_api,
                "description": "Interact with ACTiV system API",
                "type": "automation",
                "params": {"endpoint": "string"}
            },
            "browser": {
                "fn": browser_agent,
                "description": "Browse and extract web content",
                "type": "agent_tools",
                "params": {"url": "string"}
            },
            "elevenlabs": {
                "fn": elevenlabs_tts,
                "description": "Convert text to speech",
                "type": "agent_tools",
                "params": {"text": "string"}
            },
            "niflows": {
                "fn": niflows,
                "description": "Execute multi-step workflow orchestration",
                "type": "agent_tools",
                "params": {"steps": "list of dicts"}
            },
            "get_linking_code": {
                "fn": get_linking_code,
                "description": "Generate a code to link this account to other channels (like Telegram)",
                "type": "agent_tools",
                "params": {}
            }
        }

    def get_skill_descriptions(self) -> str:
        """Returns a string description of all registered skills for the Planner's prompt."""
        desc = ""
        for name, info in self.SKILLS.items():
            desc += f"- {name}: {info['description']}\n  Params: {info.get('params', {})}\n"
        return desc

    async def execute(self, name: str, permitted_categories: list = None, **kwargs) -> Any:
        """
        Executes a skill by name with provided arguments.
        All skills now take a single dictionary 'input_data'.
        'permitted_categories' allows restricting access per agent.
        """
        if name not in self.SKILLS:
            logger.warning(f"[SKILLS] Skill '{name}' not found.")
            return f"Error: Skill '{name}' not found."
        
        # Access Control Check
        skill_info = self.SKILLS[name]
        if permitted_categories and skill_info['type'] not in permitted_categories:
            logger.error(f"[SKILLS] Access Denied: Agent does not have permission for category '{skill_info['type']}'")
            return f"Error: Access Denied to skill '{name}' (Category: {skill_info['type']} is not permitted for this agent)."

        try:
            logger.info(f"[SKILLS] Executing skill: {name} (Type: {skill_info['type']})")
            # All new skills expect 'input_data' as a dictionary
            result = await skill_info["fn"](kwargs)

            
            # Standardize return for the loop (Observation string)
            if isinstance(result, dict) and "message" in result:
                return result["message"]
            return str(result)
            
        except Exception as e:
            logger.error(f"[SKILLS] Execution failed for {name}: {str(e)}")
            return f"Error executing {name}: {str(e)}"

# Singleton
registry = SkillRegistry()
