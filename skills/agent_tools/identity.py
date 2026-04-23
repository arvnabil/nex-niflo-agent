# skills/agent_tools/identity.py
import logging
from identity.linker import identity_linker

logger = logging.getLogger("nex-skills")

async def get_linking_code(input_data: dict):
    """
    Generates a unique linking code for the current user to link other channels (e.g. Telegram).
    """
    # In the Nex Platform, session_id is maped to internal_uuid 
    # But for the skill, we pass the session_id as the user's current identifier
    internal_id = input_data.get("session_id") # Note: registry.execute will pass this
    
    if not internal_id:
        return {"status": "error", "message": "Could not identify internal user ID."}

    try:
        code = identity_linker.create_registration_ticket(internal_id)
        if code == "ERROR":
            return {"status": "error", "message": "Identity service is unavailable."}
            
        return {
            "status": "success",
            "code": code,
            "message": f"KODE LINK ANDA: {code}. Silakan ketik '/link {code}' di Telegram Bot Nex untuk menghubungkan akun Anda. Kode ini berlaku selama 10 menit."
        }
    except Exception as e:
        logger.error(f"[SKILL] get_linking_code failed: {e}")
        return {"status": "error", "message": f"Identity error: {str(e)}"}

async def resolve_linking_code(input_data: dict):
    """
    Resolves a provided token to link the current channel ID to an existing internal ID.
    Used by the Telegram bot internally or via a /link command.
    """
    token = input_data.get("token")
    channel = input_data.get("channel")
    channel_id = input_data.get("channel_id")

    if not token or not channel or not channel_id:
        return {"status": "error", "message": "Missing token, channel, or channel_id."}

    internal_id = identity_linker.resolve_link_ticket(token)
    if not internal_id:
        return {"status": "error", "message": "Kode link tidak valid atau sudah kadaluarsa."}

    success = identity_linker.link_accounts(internal_id, channel, channel_id)
    if success:
        return {
            "status": "success",
            "message": "AKUN BERHASIL DIHUBUNGKAN! Selamat datang kembali. Sekarang Anda bisa melanjutkan percakapan dari channel sebelumnya."
        }
    else:
        return {"status": "error", "message": "Gagal menghubungkan akun. Silakan coba lagi."}
