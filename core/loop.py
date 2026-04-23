import asyncio
import logging
import os
import json
import re
from core.planner.planner import planner
from core.planner.parser import PlannerParser
from skills.registry import registry
from core.state import task_state
from integrations.ollama import ollama
from memory.short_term import memory_store

logger = logging.getLogger("nex-loop")

class AgentLoop:
    def __init__(self, max_steps=10):
        self.max_steps = max_steps
        self.execution_model = os.getenv("DEFAULT_MODEL", "qwen2.5:3b")

    async def run(self, session_id: str, user_input: str, agent_id: str = "sovereign"):
        state = task_state.get_or_create(session_id, user_input)
        
        # Load Agent Profile
        from agents.registry import agent_registry
        from core.supervisor.prompts import get_agent_prompt
        agent_profile = agent_registry.get_agent(agent_id)
        
        history_context = ""
        current_run_keys = [] # Track repeats ONLY within this execution
        
        logger.info(f"[LOOP] Starting agentic loop for agent '{agent_id}' in session {session_id}")

        for step in range(self.max_steps):
            logger.info(f"[LOOP] Step {step+1}/{self.max_steps}")
            
            # Fetch context from Global Memory (Shared)
            global_context = memory_store.get(session_id, segment="global")
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in global_context[-5:]])
            
            # Final Step Warning
            if step >= self.max_steps - 2:
                history_context += "\nSYSTEM NOTE: This is your FINAL reasoning step. Confim results and end the turn.\n"
            
            # 1. PLAN (Using specialized agent prompt)
            prompt = get_agent_prompt(agent_id, history_context, context_str)
            
            # 🛡️ HARD REPETITION FILTER 🛡️
            mission_input = user_input
            is_greeting_task = any(k in user_input.lower() for k in ["sapa", "greet", "tawarkan", "tanyakan", "bantu"])
            
            # Use agent name from profile to check if already introduced
            already_introduced = f"{agent_profile['name']}" in context_str or len(global_context) > 2
            
            if is_greeting_task:
                if already_introduced or any(k in user_input.lower() for k in ["error", "wifi", "kendala", "masalah", "nih"]):
                    mission_input = f"MISI: User sedang mengalami kendala spesifik. DILARANG KERAS mengulang perkenalan diri. JANGAN menyapa lagi. Langsung masuk ke solusi teknis terkait: {user_input}"
                else:
                    mission_input = f"MISI: Berikan sapaan profesional pertama Anda secara personal. JAWABLAH LANGSUNG KE PENGGUNA: {user_input}"
            
            status, action_tuple, raw_planner_output = planner.plan_step(mission_input, history_context, override_prompt=prompt)

            logger.info(f"[LOOP] RAW PLANNER OUTPUT:\n{raw_planner_output}")
            
            # 🛡️ ERROR PROTECTION: Break immediately if planner reports error
            if status == "error":
                logger.error(f"[LOOP] Planner Error: {raw_planner_output}")
                state.final_response = f"Gagal menghubungi otak saya: {raw_planner_output}"
                break

            # 2. HANDLE FINISH or CONVERSATIONAL OUTPUT
            if status == "finish" or status == "none":
                clean_res = raw_planner_output
                for header in ["THOUGHT:", "ACTION:", "THOUGHTS:", "ANALYSIS:"]:
                    if header in clean_res:
                        clean_res = clean_res.split(header)[-1].strip()
                
                # Check for finish() wrapper
                if "finish(" in clean_res:
                    # Match answer="..." or answer='...' correctly using backreference \1
                    match = re.search(r'answer=(["\'])(.*?)\1', clean_res, re.DOTALL)
                    state.final_response = match.group(2) if match else clean_res
                elif clean_res:

                    state.final_response = clean_res
                else:
                    state.final_response = "Tugas selesai, tapi saya tidak bisa merangkai kata-kata. Silakan cek detail di atas."
                
                state.is_complete = True
                break
            
            # 3. HANDLE ACTION
            if status == "action":
                skill_name, skill_args = action_tuple
                
                # 🏁 SPECIAL CASE: finish() is not a tool, it's a signal
                if skill_name == "finish":
                    state.final_response = skill_args.get("answer", raw_planner_output)
                    state.is_complete = True
                    break

                # 🛡️ VALIDATION: Check for empty arguments in tools that usually need them
                if not skill_args and skill_name != "finish":
                    logger.warning(f"[LOOP] Found action {skill_name} but with NO arguments.")
                    observation = f"ERROR: Tool '{skill_name}' requires parameters. Gunakan format ACTION: {skill_name}(topic=\"...\", datetime_iso=\"...\")"
                    history_context += f"\nTHOUGHT: {raw_planner_output}\nACTION: {skill_name}\nOBSERVATION: {observation}\n"
                    continue

                action_key = f"{skill_name}_{json.dumps(skill_args, sort_keys=True)}"
                
                # 🛡️ REPEAT DETECTION
                if action_key in current_run_keys:
                    logger.warning(f"[LOOP] Action repeat detected. Forcing finish.")
                    history_context += "\nSYSTEM: You already tried this action with these EXACT parameters! If it failed, try different parameters. If it succeeded, use finish() to report results.\n"
                    continue 
                
                current_run_keys.append(action_key)

                # 4. EXECUTE
                try:
                    # Inject session_id automatically for context-aware skills
                    skill_args["session_id"] = session_id
                    
                    observation = await registry.execute(
                        skill_name, 
                        permitted_categories=agent_profile.get("permitted_categories"),
                        **skill_args
                    )

                except Exception as e:
                    observation = f"EXECUTION ERROR: {str(e)}"

                    
                logger.info(f"[LOOP] Observation: {observation}")
                
                # Record step
                state.append_step(step + 1, action_key, raw_planner_output, skill_name, skill_args, observation)
                
                # Update context
                history_context += f"\nTHOUGHT: {raw_planner_output}\nACTION: {skill_name}\nOBSERVATION: {observation}\n"
                
                # ✨ SMART TRANSITION: If success, invite the model to finish
                if "SUCCESS" in observation:
                    history_context += "\nSYSTEM: Excellent! The task is done. Now, confirm to the user (Indonesian, warm, detail) using finish().\n"


            
            await asyncio.sleep(0.1)

        if not state.is_complete and not state.final_response:
            state.final_response = "Maximum reasoning steps reached without a final answer. Mohon coba lagi."

        logger.info(f"[LOOP] Loop complete. Final response length: {len(state.final_response)}")
        return state.final_response

# Singleton
agent_loop = AgentLoop()
