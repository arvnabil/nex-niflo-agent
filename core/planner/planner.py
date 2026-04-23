from integrations.llm import llm
from integrations.ollama import ollama # Still needed for lazy_pull check
from core.planner.prompt import get_planner_prompt
from core.planner.parser import PlannerParser
import os

class Planner:
    def __init__(self):
        self.model = os.getenv("PLANNER_MODEL", "mistral:7b")
        # Only pull if it's not an OpenAI model
        if not self.model.startswith("gpt-"):
            ollama.lazy_pull(self.model)

    def plan_step(self, user_input: str, history_context: str = "", override_prompt: str = None):
        prompt = override_prompt if override_prompt else get_planner_prompt(user_input, history_context)

        
        try:
            res = llm.chat(
                self.model, 
                [{"role": "user", "content": prompt}], 
                stream=False,
                temperature=0 # OpenAI uses temperature directly in JSON
            )
            if not self.model.startswith("gpt-") and res.status_code == 404:
                return "error", None, f"⚠️ Otak (model {self.model}) sedang diunduh di background. Mohon tunggu beberapa menit..."
            
            if res.status_code != 200:
                try:
                    err_data = res.json()
                    error_msg = err_data.get("error", {}).get("message", res.text)
                    return "error", None, f"⚠️ Masalah Koneksi: {error_msg}"
                except:
                    return "error", None, f"⚠️ Planner Error ({res.status_code})"
        except Exception as e:
            return "error", None, f"Service Connection Error: {str(e)}"
            
        # 0. Robust Parsing for different providers (Ollama vs OpenAI)
        res_data = res.json()
        if "choices" in res_data:
            # OpenAI Format
            raw_output = res_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            # Ollama Format
            raw_output = res_data.get("message", {}).get("content", "")
        
        # 1. Extract Action (Priority)
        name, args = PlannerParser.parse_action(raw_output)
        if name:
            if name == "finish":
                return "finish", (name, args), raw_output
            return "action", (name, args), raw_output
            
        # 2. Detect Finish Keyword (Fallback for simple conversational models)
        if "finish(" in raw_output.lower():
            return "finish", None, raw_output
            
        if "finish" in raw_output.lower() and "ACTION:" not in raw_output:
            return "finish", None, raw_output
            
        return "none", None, raw_output


# Singleton
planner = Planner()
