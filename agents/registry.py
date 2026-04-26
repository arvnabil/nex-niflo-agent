import logging
from typing import List, Dict, Any

logger = logging.getLogger("nex-agents")

class AgentRegistry:
    def __init__(self):
        # 🔥 UPDATED ICONS V3.1 (User Choice)
        self.AGENTS: Dict[str, Dict[str, Any]] = {
            "support": {
                "name": "Nex Support",
                "icon": "🎧", 
                "description": "Solusi Masalah Teknis & Troubleshooting.",
                "skills": ["help_desk", "troubleshoot", "n8n_workflow"]
            },
            "insight": {
                "name": "Nex Insight",
                "icon": "🧠",
                "description": "Riset Mendalam & Analisis Strategis.",
                "skills": ["web_search", "rag_search", "summarize"]
            },
            "scheduler": {
                "name": "Nex Scheduler",
                "icon": "📅",
                "description": "Manajemen Waktu & Penjadwalan Efisien.",
                "skills": ["calendar_list", "calendar_create", "zcalendar_create", "task_reminder"]
            },
            "webops": {
                "name": "Nex WebOps",
                "icon": "🌐",
                "description": "Monitoring & Integrasi API ACTiV.",
                "skills": ["activ_api", "browser", "niflows"]
            },
            "climate": {
                "name": "Nex Climate",
                "icon": "🌦️",
                "description": "Pakar Meteorologi & Analisa Rasa Cuaca.",
                "skills": ["weather_check"]
            }
        }

    def list_agents(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self.AGENTS.items()]

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        return self.AGENTS.get(agent_id.lower())

# Singleton
agent_registry = AgentRegistry()
