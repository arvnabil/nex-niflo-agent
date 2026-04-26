import json
import logging
import re
import os
from typing import Dict, Any
from integrations.llm import llm
from agents.registry import agent_registry

logger = logging.getLogger("nex-v2-supervisor")

class NexSupervisor:
    """The High-Level Router V2.8.6: Personalized Agent Intros."""
    
    ACTION_KEYWORDS = [
        (r"jadwal|agenda|kalend[ae]r|skedul|reminder", "Kalender"),
        (r"meeting|zoom|rapat|konferensi", "Meeting"),
        (r"email|surel|emael", "Email"),
        (r"cuaca|hujan|panas|dingin|suhu|weather", "Cuaca"),
        (r"error|wifi|rusak|bantu|troubleshoot", "Support"),
        (r"analisa|riset|cek data|cek histori", "Insight"),
        (r"web|api|monitoring", "WebOps"),
        (r"agent|agen|squad|fitur|kemampuan|bisa apa", "Agent Query")
    ]
    
    GREETING_KEYWORDS = [r"^halo$", r"^hai$", r"^hi$", r"^p$", r"^ping$"]

    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.model = os.getenv("PLANNER_MODEL", "gpt-4o")

    def _extract_context(self, text: str) -> str:
        for pattern, label in self.ACTION_KEYWORDS:
            if re.search(pattern, text.lower()): return label
        return "Permintaan Lu"

    async def route(self, user_input: str, history: str = "") -> Dict[str, Any]:
        """Routes with personalized agent name mentions."""
        logger.info(f"[SUPERVISOR-V2.8.6] Routing input: {user_input[:50]}...")
        
        try:
            # Quick check for greetings
            if any(re.search(p, user_input.lower().strip()) for p in self.GREETING_KEYWORDS):
                return {
                    "routing": {"intent": "conversational", "soft_confirmation": "Halo Bro Nabil! Ada tim yang mau Lu kerahkan? 🚀"},
                    "plan": []
                }

            user_input_lower = user_input.lower()
            context = self._extract_context(user_input_lower)
            
            must_route_patterns = [r"agent", r"agen", r"squad", r"fitur", r"bisa apa", r"kemampuan"]
            is_agent_query = any(re.search(p, user_input_lower) for p in must_route_patterns)
            
            is_generic_action = False
            for pattern, _ in self.ACTION_KEYWORDS:
                if re.search(pattern, user_input_lower):
                    is_generic_action = True
                    break
            
            if is_agent_query or is_generic_action:
                mapping = {
                    "Support": "support", "Insight": "insight", "Kalender": "scheduler",
                    "Meeting": "scheduler", "WebOps": "webops", "Cuaca": "climate",
                    "Agent Query": "insight"
                }
                target_id = mapping.get(context, "insight")
                agent_info = agent_registry.get_agent(target_id)
                agent_name = agent_info.get("name", "Nex Agent")
                
                # 🔥 PERSONALIZED INTRO (V2.8.6)
                if is_agent_query:
                    soft_msg = f"Siap Bro, gue tampilkan status **SQUAD** sekarang! 🛡️"
                else:
                    # Ganti "gerakkan tim" jadi "panggilin [Nama Agen]"
                    soft_msg = f"Siap Bro, gue panggilin {agent_name} buat urusan {context}! 🚀"
                
                return {
                    "routing": {
                        "intent": "routing",
                        "soft_confirmation": soft_msg
                    },
                    "plan": [{"id": "T1", "agent": target_id, "task": user_input, "dependencies": []}]
                }
            
            smart_response = await self._generate_smart_response(user_input, history)
            return {"routing": {"intent": "conversational", "soft_confirmation": smart_response}, "plan": []}
            
        except Exception as e:
            logger.error(f"[SUPERVISOR-V2.8.6] Error: {e}")
            return {"routing": {"intent": "conversational", "soft_confirmation": "Radar gue lagi glitcing, Bro."}, "plan": []}

    async def _generate_smart_response(self, user_input: str, history: str) -> str:
        prompt = f"Nex Sovereign mode. Bro-style. Direct. Sebut Bro Nabil. HISTORY: {history}\nUSER: {user_input}"
        res = llm.chat(self.model, [{"role": "user", "content": prompt}])
        return res.json().get("choices", [{}])[0].get("message", {}).get("content", "Ada apa, Bro?")
