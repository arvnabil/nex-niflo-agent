import json

class IntentAgent:
    def __init__(self):
        self.system_prompt = """
You are Nex Intent Engine.
Your job is to DETECT USER INTENT and RETURN STRUCTURED JSON.

## 🧠 MODES
You ONLY respond in JSON.

1. NORMAL CHAT (NO ACTION)
{
  "intent": "none",
  "response": "..."
}

2. ACTION INTENT
{
  "intent": "create_zoom_meeting",
  "confidence": 0.0-1.0,
  "params": {
    "topic": "...",
    "datetime": "...",
    "duration": 60
  }
}

3. KNOWLEDGE SEARCH (RAG)
{
  "intent": "knowledge_search",
  "query": "..."
}

## 🔥 SUPPORTED INTENTS
- create_zoom_meeting (keywords: meeting, zoom, jadwal, schedule)
- knowledge_search (keywords: menurut dokumen, apa kata file, cari di data, penjelasan tentang [X])

## 🧠 RULES
- ALWAYS return JSON.
- NEVER explain or add text outside JSON.
- If unsure, return intent: none.
"""

    def get_prompt(self, user_persona=""):
        return f"{self.system_prompt}\n\n--- USER PERSONA ---\n{user_persona}"

    def parse_response(self, raw_output):
        try:
            # Clean possible markdown code blocks
            clean_output = str(raw_output).strip()
            if "```" in clean_output:
                parts = clean_output.split("```")
                for part in parts:
                    p = part.strip()
                    if p.startswith("json"): p = p[4:].strip()
                    if p.startswith("{") and p.endswith("}"):
                        clean_output = p
                        break
            return json.loads(clean_output)
        except:
            return {"intent": "none", "response": str(raw_output).strip()}

# Singleton
intent_agent = IntentAgent()
