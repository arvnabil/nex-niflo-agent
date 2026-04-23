# skills/agent_tools/elevenlabs.py
import os
import httpx
import logging

logger = logging.getLogger("nex-skills")

async def elevenlabs_tts(input_data: dict):
    """
    Converts text to speech using ElevenLabs API.
    Params: text (string), voice_id (string, optional)
    """
    text = input_data.get("text")
    if not text:
        return {"status": "error", "message": "No text provided for audio generation"}

    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = input_data.get("voice_id", "pNInz6obpg8nEmeW44vX") # Default voice

    if not api_key:
        logger.warning("[SKILLS] ELEVENLABS_API_KEY missing. Returning placeholder.")
        return {
            "status": "success",
            "message": "Audio generated (Simulation: ElevenLabs Key missing).",
            "data": {"text": text, "simulation": True}
        }

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=data, timeout=30.0)
            if res.status_code == 200:
                # In a real scenario, you'd save this to a file or stream it
                return {
                    "status": "success",
                    "message": "Audio successfully generated via ElevenLabs.",
                    "data": {"size": len(res.content)}
                }
            else:
                return {
                    "status": "error",
                    "message": f"ElevenLabs API error: {res.status_code} - {res.text[:100]}"
                }
    except Exception as e:
        return {"status": "error", "message": f"ElevenLabs TTS failed: {str(e)}"}
