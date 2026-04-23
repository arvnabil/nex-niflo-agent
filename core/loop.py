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
    def __init__(self, max_steps=15):
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
            
            # 🛡️ ANTI-GRAVITY PROTOCOL: Mission Focus
            # We no longer force greetings. The agent persona and Supervisor command 
            # should dictate the behavior.
            mission_input = user_input
            
            # Simple context check for repetition prevention
            if f"{agent_profile['name']}" in context_str:
                mission_input = f"MISI LANJUTAN: JANGAN mengulang perkenalan. Fokus pada tugas teknis: {user_input}"
            
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
                    
                    # 🚀 OPERATIONAL LOG (HIGH VISIBILITY)
                    logger.warning("="*50)
                    logger.warning(f"🎯 EXECUTING TOOL: {skill_name}")
                    logger.warning(f"📦 ARGS: {skill_args}")
                    logger.warning("="*50)

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
                



                            # ✨ CONTEXT-AWARE TRANSITION: Invite to finish if observation contains success 
                # but only after checking that we've reached a useful state.
                if "SUCCESS" in observation:
                    history_context += "\nSYSTEM: Sepertinya tugas sudah tuntas. Jika tidak ada lagi yang perlu dilakukan, segera laporkan ke user menggunakan finish().\n"

            await asyncio.sleep(0.1)

        # 🎯 FINAL POLISH: Ensure we have a decent message even if max_steps hit
        if not state.final_response:
            if state.steps:
                last_obs = state.steps[-1].get("observation", "")
                if "Berhasil" in last_obs or "SUCCESS" in last_obs:
                    state.final_response = last_obs # Use the tool's success message as final
                else:
                    state.final_response = "Tugas sedang diproses di latar belakang. Silakan cek sistem Anda dalam beberapa saat."
            else:
                state.final_response = "Maaf, Nex sedang kesulitan memproses permintaan ini. Bisa diulangi dengan bahasa yang lebih sederhana?"

        logger.info(f"[LOOP] Loop complete. Final response length: {len(state.final_response)}")
        
        # Final Clean-up of any leaking tags or repetitive greetings
        final_text = state.final_response
        final_text = re.sub(r"<(thought|analysis)>.*?</\1>", "", final_text, flags=re.DOTALL | re.IGNORECASE)
        final_text = re.sub(r"(THOUGHT|ANALYSIS|STEP|ACTION):", "", final_text, flags=re.IGNORECASE).strip()
        
        # 🟢 TELEGRAM COMPATIBILITY: Convert Markdown Headers (#, ##, ###) even if not at start of line
        final_text = re.sub(r"#+\s*(.*)", r"**\1**", final_text)
        
        # Anti-HelpDesk Filter: Just remove the specific greetings instead of splitting the whole text
        greetings = ["Apa yang bisa saya bantu", "Apakah Anda ingin mengetahui cuaca", "Apakah ada hal lain"]
        for g in greetings:
            if g in final_text and len(final_text) > 100: # Only clear if text is already long
                final_text = final_text.replace(g, "").strip()
                # Clean up trailing punctuation after removal
                final_text = re.sub(r"[\?\.\!\s]+$", "", final_text).strip()
        
        return final_text

# Singleton
agent_loop = AgentLoop()
