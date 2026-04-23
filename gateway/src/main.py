import os
import time
import json
import logging
import requests
import asyncio
import uuid
from fastapi import FastAPI, Request, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from typing import List, Optional

# Core Imports
from core.supervisor.sovereign import sovereign
from identity.linker import identity_linker
from memory.short_term import memory_store
from integrations.ollama import ollama
from observability.logger import observability
from skills.registry import registry
from agents.registry import agent_registry

# 🪵 LOGGING SETUP
logger = logging.getLogger("nex-gateway")

# 🚀 APP INITIALIZATION
app = FastAPI(title="Nex Enterprise AI Platform")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 🔐 SECURITY SETUP
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
NEX_API_KEY = os.getenv("NEX_API_KEY", "nex-sovereign-key-2026")

async def verify_api_key(request: Request, api_key_query: str = Depends(api_key_header)):
    if api_key_query == NEX_API_KEY: return api_key_query
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.replace("Bearer ", "") == NEX_API_KEY: return NEX_API_KEY
    raise HTTPException(status_code=403, detail="Invalid API Key")

# 📦 MODELS
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False

# 🧩 SSE HELPER (OpenAI compatible)
async def openai_streamer(user_id, user_input, channel="web"):
    try:
        # Initial chunk to establish assistant role
        yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {'role': 'assistant'}}]})}\n\n"
        
        internal_id = identity_linker.get_internal_id(channel, user_id)
        
        # 🧠 SYNC MEMORY IMMEDIATELY
        history = memory_store.get(internal_id, segment="global")
        history.append({"role": "user", "content": user_input, "channel": channel})
        memory_store.save(internal_id, history[-10:], segment="global")
        
        full_response = ""
        
        # Use the generator with dynamic speaker (model label) support
        async for speaker, chunk in sovereign.process_request(internal_id, user_input, channel=channel):
            full_response += chunk
            model_label = f"nex-{speaker.replace('_', '-')}"
            
            # 🛡️ ROBUST STREAMING: Yield full chunks and fix escaped newlines
            clean_chunk = chunk.replace("\\n", "\n")
            yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {'content': clean_chunk}}], 'model': model_label})}\n\n"
            await asyncio.sleep(0.05)
            
            # Separator logic between chunks (if multiple steps)
            if speaker == "sovereign":
                await asyncio.sleep(0.3)
                newline_payload = json.dumps({
                    'choices': [{'index': 0, 'delta': {'content': '\n\n---\n\n'}}],
                    'model': model_label
                })
                yield f"data: {newline_payload}\n\n"

        # Save the final full response to memory
        history = memory_store.get(internal_id, segment="global")
        history.append({"role": "assistant", "content": full_response})
        memory_store.save(internal_id, history[-10:], segment="global")
            
        yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"[GATEWAY] Stream Error: {e}")
        yield f"data: {json.dumps({'choices': [{'index': 0, 'delta': {'content': f'Error: {str(e)}'}}]})}\n\n"
        yield "data: [DONE]\n\n"

# 🛣️ ROUTES
@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
@limiter.limit("20/minute")
async def chat_completions(request: Request, body: ChatRequest):
    user_input = body.messages[-1].content if body.messages else ""
    user_id = f"web_{str(uuid.uuid4())[:8]}" 
    
    if body.stream:
        return StreamingResponse(openai_streamer(user_id, user_input, "web"), media_type="text/event-stream")
    
    # Non-streaming fallback
    internal_id = identity_linker.get_internal_id("web", user_id)
    chunks = []
    last_speaker = "sovereign"
    async for speaker, chunk in sovereign.process_request(internal_id, user_input, channel="web"):
        chunks.append(chunk)
        last_speaker = speaker
    
    response = "\n\n".join(chunks)
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "choices": [{"message": {"role": "assistant", "content": response}, "finish_reason": "stop"}],
        "model": f"nex-{last_speaker.replace('_', '-')}"
    }

@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    try:
        msg = update.get("message", {})
        chat_id = str(msg.get("chat", { }).get("id"))
        text = msg.get("text", "").strip()
        if not text or not chat_id: return {"ok": True}

        internal_id = identity_linker.get_internal_id("telegram", chat_id)
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # ⚡ COMMAND HANDLER
        if text.startswith("/"):
            command = text.split(" ")[0].lower()
            response_text = ""
            
            if command == "/skills":
                response_text = "🎯 *Daftar Skill Nex Niflo:*\n\n" + registry.get_skill_descriptions()
            elif command == "/activwebsite" or command == "/activ":
                portal = os.getenv("NEX_PUBLIC_URL", "http://localhost:8000")
                response_text = f"🌐 *Nex Portal:* [Klik di sini]({portal})\nSistem integrasi ACTiV sedang online."
            elif command == "/agent" or command == "/status":
                active_squad = "\n".join([f"• {a['name']}" for a in agent_registry.list_agents()])
                response_text = f"🛡️ *Nex Agent Status:*\n- OS: Nex Core v2.0\n- Protocol: Anti-Gravity (Zero Generic Mode)\n- Status: Operational (WIB)\n\n👥 *Nex Agent Squad [Active]:*\n{active_squad}"
            elif command == "/help" or command == "/start":
                response_text = "🤖 *Nex Telegram Assistant*\n\nGunakan perintah berikut:\n/skills - Daftar kemampuan saya\n/activwebsite - Link portal ACTiV\n/agent - Status sistem\n/help - Bantuan ini\n\nAtau langsung chat saja untuk tanya apapun!"
            
            if response_text and bot_token:
                requests.post(url, json={"chat_id": chat_id, "text": response_text, "parse_mode": "Markdown"})
                return {"ok": True}
        
        # 🛡️ TELEGRAM AGGREGATOR: Send one bubble per speaker to avoid flooding
        current_speaker = None
        speaker_buffer = ""
        full_response = ""
        
        # Show typing indicator
        if bot_token:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

        async for speaker, chunk in sovereign.process_request(internal_id, text, channel="telegram"):
            full_response += chunk
            if current_speaker is None:
                current_speaker = speaker
            
            # If the speaker changes (e.g. Sovereign -> Help Desk), flush the buffer
            if speaker != current_speaker:
                if speaker_buffer.strip() and bot_token:
                    requests.post(url, json={"chat_id": chat_id, "text": speaker_buffer.strip(), "parse_mode": "Markdown"})
                speaker_buffer = chunk
                current_speaker = speaker
            else:
                speaker_buffer += chunk

        # Final flush for the last speaker's message
        if speaker_buffer.strip() and bot_token:
            requests.post(url, json={"chat_id": chat_id, "text": speaker_buffer.strip(), "parse_mode": "Markdown"})
        
        # Save full interaction to memory (for omnichannel consistency)
        history = memory_store.get(internal_id, segment="global")
        history.append({"role": "user", "content": text, "channel": "telegram"})
        history.append({"role": "assistant", "content": full_response})
        memory_store.save(internal_id, history[-10:], segment="global")

        return {"ok": True}
    except Exception as e:
        logger.error(f"[TELEGRAM] Webhook error: {e}")
        return {"ok": False}

@app.get("/health")
async def health():
    return {"status": "omnichannel_ready", "supervisor": "sovereign", "agents": 6}

# 🚀 STARTUP
@app.on_event("startup")
async def startup():
    logger.info("Nex Enterprise AI Platform is ONLINE")
    # Warm up models if needed
