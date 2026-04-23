import logging
import httpx
import os
from typing import Dict, Any

logger = logging.getLogger("nex-skills")

async def zcalendar_create(input_data: Dict[str, Any]):
    """
    Super-Skill: Calls the n8n Orchestrator (nex-gc-zoom) to handle everything.
    """
    topic = input_data.get("topic", "Meeting Nex")
    
    # Ambil start_time dari salah satu alias yang mungkin dikirim AI
    start_time = input_data.get("start_time") or input_data.get("datetime_iso")
    
    host_email = input_data.get("host_email", "support@activ.co.id")

    if not start_time:
        logger.error("[ORCHESTRATOR] Gagal mengirim: start_time kosong!")
        return {"status": "error", "message": "Maaf, Nex gagal menentukan jam meeting. Mohon sebutkan jamnya dengan jelas."}
    
    # URL Orchestrator baru Anda
    webhook_url = os.getenv("N8N_ORCHESTRATOR_URL", "http://nex-niflo-agent-n8n:5678/webhook/nex-gc-zoom")

    logger.warning(f"[ORCHESTRATOR] Sending mission to: {webhook_url}")

    payload = {
        "skill": "zcalendar_hybrid",
        "params": {
            "topic": topic,
            "start_time": start_time,
            "host_email": host_email
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            res = await client.post(webhook_url, json=payload)
            if res.status_code == 200:
                res_data = res.json()
                # n8n Orchestrator sudah memformat pesan di node 'Format Response'
                return {"status": "success", "message": res_data.get("message", "✅ Meeting & Kalender berhasil dibuat melalui Orchestrator.")}
            else:
                return {"status": "error", "message": f"Orchestrator n8n error ({res.status_code})"}
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Critical failure: {str(e)}")
            return {"status": "error", "message": f"Gagal menghubungi Orchestrator n8n: {str(e)}"}
