import os
import logging
import asyncio
import re
import json
from datetime import datetime
from typing import AsyncGenerator, List, Dict, Any
from .agent import NexAgent
from .tools import ToolManager
from integrations.llm import llm
from agents.registry import agent_registry

logger = logging.getLogger("nex-v2-executor")

class MissionExecutor:
    """The V3.10 Precision Engine: Clean Topic Extraction."""
    
    ACTION_MAP = [
        (r"jadwal|agenda|kalend[ae]r|skedul", "Kalender"),
        (r"meeting|zoom|rapat|konferensi", "Meeting"),
        (r"email|surel|emael", "Email"),
        (r"cuaca|hujan|panas|dingin|weather", "Cuaca"),
        (r"error|wifi|rusak|bantu|troubleshoot", "Support")
    ]
    
    def __init__(self, agent: NexAgent, tool_manager: ToolManager):
        self.agent = agent
        self.tools = tool_manager
        self.max_steps = 5
        self.model = os.getenv("PLANNER_MODEL", "gpt-4o")

    def _get_context(self, task: str) -> str:
        for p, label in self.ACTION_MAP:
            if re.search(p, task.lower()): return label
        return "permintaan Lu"

    def _check_ambiguity(self, task: str) -> bool:
        task_lower = task.lower().strip()
        ambiguous_patterns = [
            r"^buat meeting$", r"^jadwalkan call$", r"^agenda besok$", 
            r"^meeting sama tim$", r"^buat jadwal$", r"^set meeting$",
            r"^bikin meeting$"
        ]
        if any(re.search(p, task_lower) for p in ambiguous_patterns):
            return True
        return False

    def _has_enough_info(self, task: str) -> bool:
        task_lower = task.lower().strip()
        has_time = any(kw in task_lower for kw in ["jam", "pukul", "sore", "pagi", "siang", "malam", "besok", "hari ini", "tanggal"])
        is_generic = task_lower in ["buat meeting", "bikin meeting", "buat jadwal", "meeting"]
        return has_time and not is_generic

    def _generate_clarification_message(self, task: str) -> str:
        return (
            "Bro, gue bantu set ini ya — tapi gue perlu konfirmasi dikit:\n\n"
            "Mau:\n"
            "1. 📅 Cuma dicatet di kalender\n"
            "2. 🎥 Cuma dibikinin link meeting (Zoom)\n"
            "3. 🚀 Bikin Meeting (zoom) dan catet kalender\n\n"
            "Ketik angka (1 / 2 / 3) atau jelasin dikit biar gue langsung eksekusi ⚡"
        )

    async def run_mission_stream(self, task: str, history: str = "", state: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """Runs mission with V3.10 Smart Merging."""
        action = None
        current_task = task
        forced_tool = None
        
        # 🛡️ 0. RESOLVE PENDING STATES (V3.10)
        if state and state.get("pending_clarification"):
            pending = state["pending_clarification"]
            
            if pending["type"] == "meeting_or_calendar":
                decision = None
                task_lower = task.lower().strip()
                if task_lower == "1": decision = "calendar_create"
                elif task_lower == "2": decision = "zoom_engineer"
                elif task_lower == "3": decision = "zcalendar_create"
                
                if decision:
                    original_task = pending["original_task"]
                    if self._has_enough_info(original_task):
                        forced_tool = decision
                        current_task = original_task
                        state["pending_clarification"] = None
                    else:
                        state["pending_clarification"] = {"type": "slot_filling", "tool": decision, "original_task": original_task}
                        yield f"Oke Bro, Gue perlu informasi nih nama topik, jam dan tanggal nya kapan bro hari ini atau besok dll"
                        return
                else:
                    if "catet" in task_lower or "kalender" in task_lower: decision = "calendar_create"
                    elif "zoom" in task_lower or "link" in task_lower: decision = "zoom_engineer"
                    elif "dua-duanya" in task_lower or "hybrid" in task_lower: decision = "zcalendar_create"
                    if decision:
                        forced_tool = decision
                        current_task = f"{pending['original_task']} {task}"
                        state["pending_clarification"] = None
                    else:
                        yield "Ketik angka **1, 2, atau 3** biar gue langsung gas! 🙏"
                        return
            
            elif pending["type"] == "slot_filling":
                # 🔥 V3.10 FIX: Merge but let LLM extract clean params
                current_task = f"{pending['original_task']} {task}"
                forced_tool = pending["tool"]
                state["pending_clarification"] = None
                logger.info(f"[EX-V3.10] slots filling resolved into: {current_task}")

        # 🛡️ 1. TRIGGER INITIAL CLARIFICATION
        if not action and not forced_tool and self.agent.agent_id == "scheduler" and self._check_ambiguity(current_task):
            if state is not None:
                state["pending_clarification"] = {"type": "meeting_or_calendar", "original_task": current_task}
                yield self._generate_clarification_message(current_task)
                return

        tools_desc = self.tools.get_descriptions()
        system_prompt = self.agent.get_system_prompt(tools_desc)
        messages = [{"role": "system", "content": system_prompt}]
        
        final_result = None
        is_specialized = self.agent.agent_id in ["climate", "scheduler"]

        for step in range(self.max_steps):
            if not action:
                # Add instruction to LLM to take the forced tool choice seriously
                user_msg = f"TASK: {current_task}"
                if forced_tool:
                    user_msg += f"\nDECISION: Please execute '{forced_tool}' with cleaned parameters extracted from the task."
                
                chat_msgs = messages + [{"role": "user", "content": user_msg}]
                res = llm.chat(self.model, chat_msgs)
                if res.status_code != 200:
                    yield "⚠️ Koneksi pusat lagi glitch."
                    return
                llm_output = res.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                action = self.agent.extract_action(llm_output)
            
            # 🔥 FALLBACKS (If LLM fails to provide action)
            if not action and step == 0:
                task_lower = current_task.lower()
                target_tool = forced_tool if forced_tool else ("zcalendar_create" if "meeting" in task_lower else "calendar_create")
                action = {"tool": target_tool, "params": {"topic": current_task}}

            if action:
                # Ensure the tool chosen by LLM matches the forced_tool intent if coming from clarification
                if forced_tool and action["tool"] != forced_tool:
                    logger.warning(f"[EX-V3.10] LLM tried to detour to {action['tool']} but we forced {forced_tool}")
                    action["tool"] = forced_tool

                result = await self.tools.execute(action["tool"], action["params"])
                raw_msg = result.get("message", "")
                
                if result.get("status") == "success":
                    if is_specialized:
                        if self.agent.agent_id == "climate" or "weather" in str(action["tool"]):
                            final_result = await self._generate_unified_weather_report(current_task, raw_msg)
                        elif self.agent.agent_id == "scheduler" or "zoom" in str(action["tool"]) or "calendar" in str(action["tool"]):
                            final_result = await self._generate_unified_scheduler_report(current_task, raw_msg)
                    else:
                        final_result = self.format_final_answer(result)
                    break
                else:
                    logger.warning(f"[EX-V3.8] Tool execution failed: {raw_msg}")
                    final_result = f"🚨 **Error Eksekusi!**\nSistem n8n Lu menolak perintah gue.\n\n`Log: {raw_msg}`\n\nCoba cek jalur internet atau settingan n8n Lu ya, Bro! 🙏"
                    break

            finish_msg = self.agent.detect_finish(llm_output)
            if finish_msg:
                if is_specialized and any(kw in current_task.lower() for kw in ["kalend", "zoom", "meeting", "rapat"]):
                    continue
                final_result = finish_msg
                break
            messages.append({"role": "assistant", "content": llm_output})

        if final_result:
            yield final_result
            await asyncio.sleep(0.5)
            yield "[SPLIT]"
            yield "Okey Bro Nabil, gue stand-by buat bantuan berikutnya! ☕️🚀"
        else:
            yield f"🚨 **Sori Bro Nabil, Gue Mentok!** 🙏🚀"

    async def _generate_unified_scheduler_report(self, task: str, raw_data: str) -> str:
        data_block = raw_data
        json_match = re.search(r"\{.*\}", raw_data)
        if json_match: data_block = json_match.group(0)
        
        prompt = (
            f"# DATA: {data_block}\n"
            f"# TASK: {task}\n"
            "Buat konfirmasi PREMIUM dengan format SAMA PERSIS seperti di bawah ini, "
            "JANGAN gunakan judul # (Markdown Header), JANGAN gunakan garis pemisah (---). "
            "Ekstrak data dari JSON yang tersedia.\n\n"
            "📍 Konfirmasi Penjadwalan Nex Scheduler Hybrid\n"
            "Halo, permintaan Anda telah berhasil dieksekusi oleh sistem. Berikut adalah rincian jadwal meeting yang telah tersinkronisasi ke Zoom dan Google Calendar:\n\n"
            "📅 Meeting Berhasil Dibuat!\n\n"
            "📝 Topik: [Isi Topik]\n"
            "⏰ Waktu: [Hari, Tanggal Bulan Tahun pukul Jam.Menit WIB]\n"
            "🔑 Passcode: [Isi Passcode]\n"
            "🆔 Meeting ID: [Isi Meeting ID]\n"
            "🔗 Link Meeting: [Isi URL Link Zoom Langsung, jangan di-hide]\n"
            "🧑💻 Host: [Isi Email Host]\n\n"
            "📌 Catatan: Harap join 5 menit sebelum dimulai.\n\n"
            "Stay [1 kata] [icon]"
        )
        try:
            res = llm.chat(self.model, [{"role": "user", "content": prompt}])
            content = res.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            # Remove any leaking markdown headers or separators if LLM misses
            content = re.sub(r"^#+.*", "", content, flags=re.MULTILINE)
            content = re.sub(r"^-{3,}", "", content, flags=re.MULTILINE)
            return content.strip()
        except: return f"Berhasil dijadwalkan! {raw_data}"

    async def _generate_unified_weather_report(self, task: str, raw_data: str) -> str:
        prompt = f"# DATA: {raw_data}\nlaporan cuaca premium singkat. Stay Connected! ☕️🚀😎"
        try:
            res = llm.chat(self.model, [{"role": "user", "content": prompt}])
            return res.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except: return raw_data

    def format_final_answer(self, result: dict) -> str:
        msg = result.get('message', '')
        return msg.replace("CALENDAR_SUCCESS | ", "").replace("Action: Create | ", "") or "Selesai!"
