from agents.intent_agent import intent_agent
from integrations.ollama import ollama
from rag.generation.rag_chain import rag_chain
from skills.zoom_meeting import zoom_meeting
from memory.short_term import memory_store
import os
import json

class Orchestrator:
    def __init__(self):
        self.model = os.getenv("DEFAULT_MODEL", "qwen2.5:3b")

    def process(self, session_id, user_input, system_persona=""):
        # 1. Get History
        history = memory_store.get_session(session_id)
        
        # 2. Intent Detection
        intent_payload = [
            {"role": "system", "content": intent_agent.get_prompt(system_persona)},
            {"role": "user", "content": user_input}
        ]
        
        res = ollama.chat(self.model, intent_payload, stream=False)
        if res.status_code != 200:
            return f"Brain Error: {res.status_code}"
            
        parsed = intent_agent.parse_response(res.json().get("message", {}).get("content", ""))
        intent = parsed.get("intent", "none")
        
        # 3. Execution Hub
        response_text = ""
        
        if intent == "create_zoom_meeting":
            status, result = zoom_meeting.execute(parsed.get("params", {}))
            if status == 200:
                response_text = f"✅ Zoom meeting created successfully.\n\nDetails: {json.dumps(parsed.get('params'), indent=2)}"
            else:
                response_text = f"❌ Failed to create meeting: {result}"
                
        elif intent == "knowledge_search":
            rag_response = rag_chain.generate_with_context(parsed.get("query", user_input))
            response_text = rag_response or f"No specific local knowledge found for: {user_input}"
            
        else:
            # Normal Chat path
            response_text = parsed.get("response") or "I'm not sure how to help with that."
        
        # 4. Save History
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response_text})
        memory_store.save_session(session_id, history[-10:])
        
        return response_text

# Singleton
orchestrator = Orchestrator()
