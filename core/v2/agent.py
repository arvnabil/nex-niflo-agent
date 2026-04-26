import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("nex-v2-agent")

class NexAgent:
    """The high-pressure thinking engine V3.2.3: Calendar Enforcer."""
    
    def __init__(self, agent_id: str, persona: str, llm_client=None):
        self.agent_id = agent_id
        self.persona = persona
        self.llm = llm_client

    def extract_action(self, llm_output: str) -> Optional[Dict[str, Any]]:
        match = re.search(r"ACTION:\s*([a-zA-Z0-9_]+)\((.*?)\)", llm_output, re.DOTALL)
        if not match: return None
        tool_name = match.group(1).strip()
        params_str = match.group(2).strip()
        params = {}
        for kv in re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|([^,)\s]+))', params_str):
            key = kv[0]
            val = kv[1] if kv[1] is not None and kv[1] != "" else kv[2]
            params[key] = val
        return {"tool": tool_name, "params": params}

    def detect_finish(self, llm_output: str) -> Optional[str]:
        match = re.search(r"finish\((?:answer=)?[\"'](.*?)[\"']\)", llm_output, re.DOTALL)
        return match.group(1) if match else None

    def get_system_prompt(self, tools_desc: str) -> str:
        """The Nex Command Protocol V3.2.3: Anti-Hallucination & Tool Mandate."""
        now = datetime.now()
        current_time_str = now.strftime("%A, %d %B %Y - %H:%M WIB")

        return f"""
# IDENTITY & STYLE
{self.persona}
- Gaya Bahasa: Santai, Bro-style, Sat-set.

# 🕒 TEMPORAL CONTEXT
- WAKTU SEKARANG: {current_time_str}

# 🔱 SCHEDULING DOCTRINE (MANDATORY)
1. ZOOM/MEETING: Jika ada kata "Meeting", "Zoom", "Rapat" -> WAJIB ACTION `zcalendar_create`.
2. GOOGLE CALENDAR ONLY: Jika hanya "Kalender", "Jadwal", "Agenda", "Reminder" (tanpa Zoom) -> WAJIB ACTION `calendar_create`.
3. DILARANG KERAS memberikan jawaban "Sudah saya catat/set" tanpa memanggil TOOL terlebih dahulu.
4. JAWABAN PERCAKAPAN HANYA BOLEH SETELAH TOOL SELESAI EKSEKUSI.

# 🛡️ HONESTY PROTOCOL
Jika tool tidak ada, gunakan `finish(answer="...")`.

# 🚨 EXECUTION RULE
- Turn 1 WAJIB ACTION. NO CHAT.
- Format: `ACTION: tool_name(key="value")`

# AVAILABLE TOOLS
{tools_desc}
"""
