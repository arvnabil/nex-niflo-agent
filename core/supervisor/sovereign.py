import json
import logging
from integrations.llm import llm
from core.supervisor.prompts import get_supervisor_prompt
from core.supervisor.executor import dag_executor
import os

logger = logging.getLogger("nex-sovereign")

class SovereignSupervisor:
    """
    The Single Brain of Nex Squad.
    Handles Routing, Confidence Logic, and Coordination.
    """
    def __init__(self):
        self.model = os.getenv("PLANNER_MODEL", "gpt-4o")

    async def process_request(self, session_id: str, user_input: str, channel: str = "web"):
        """
        Generator version to support '2-step' responses with dynamic model labels.
        Yields tuples of (speaker_id, content).
        """
        logger.info(f"[SOVEREIGN] Processing request from channel: {channel}")
        
        # 1. BRAIN: Route & Plan
        prompt = get_supervisor_prompt(user_input)
        res = llm.chat(self.model, [{"role": "user", "content": prompt}])
        
        if res.status_code != 200:
            yield ("sovereign", "Maaf, otak saya sedang dalam pemeliharaan. Silakan coba lagi nanti.")
            return

        raw_output = res.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        
        try:
            # Enhanced JSON cleaning
            clean_json = raw_output.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            # Truncate at brackets
            if "{" in clean_json and "}" in clean_json:
                clean_json = clean_json[clean_json.find("{"):clean_json.rfind("}")+1]
            
            data = json.loads(clean_json)
            routing = data.get("routing", {})
            plan = data.get("plan", [])
            
            confidence = routing.get("confidence", 0.0)
            logger.info(f"[SOVEREIGN] Intent: {routing.get('intent')} | Confidence: {confidence}")

            # 2. CONVERSATIONAL & GREETING PATH
            if routing.get("intent") == "conversational" and not routing.get("selected_agents"):
                yield ("sovereign", routing.get("soft_confirmation", "Halo! Ada yang bisa saya bantu hari ini?"))
                return

            # 3. INTERMEDIATE RESPONSE (Soft Confirmation)
            soft_confirm = routing.get("soft_confirmation", "")
            if soft_confirm:
                yield ("sovereign", f"{soft_confirm}\n\n")
            elif confidence < 0.5:
                yield ("sovereign", f"Saya belum sepenuhnya menangkap maksud Anda. Apakah Anda ingin {routing.get('intent', 'melakukan sesuatu')}? Mohon berikan detail lebih lanjut.")
                return

            # 4. EXECUTE PLAN (Only if confidence is high enough or it's a valid plan)
            if plan:
                results = await dag_executor.execute(session_id, plan)
                
                # Use the last agent's ID for the final response speaker label
                last_agent_id = plan[-1]['agent'] if plan else "sovereign"
                
                # 5. SYNTHESIZE & RETURN FINAL
                final_answer = await self.synthesize_response(user_input, results, channel, None)
                yield (last_agent_id, final_answer)
            elif not soft_confirm:
                yield ("sovereign", "Tugas diterima, namun saya belum menyusun rencana eksekusi. Ada hal spesifik yang ingin dilakukan?")

        except Exception as e:
            logger.error(f"[SOVEREIGN] Error parsing supervisor output: {e}")
            yield ("sovereign", raw_output if len(raw_output) > 20 else "Ada kesalahan teknis dalam memproses rencana tugas.")

    async def synthesize_response(self, user_input, results, channel, soft_confirm):
        """
        Menggabungkan hasil kerja agen menjadi jawaban yang kohesif.
        """
        if not results:
            return soft_confirm if soft_confirm else "Eksekusi selesai, namun tidak ada laporan hasil yang diterima."

        if len(results) == 1:
            return str(results[0]).strip()
        
        res_str = "\n\n".join([f"{r}" for r in results])
        return f"{res_str}"

# Singleton
sovereign = SovereignSupervisor()
