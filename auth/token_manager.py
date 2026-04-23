import httpx
import os
import time
import logging
import json
from memory.short_term import memory_store

logger = logging.getLogger("nex-auth")

class TokenManager:
    """
    Centralized Token Management Service (The Single Source of Truth).
    Managed by Sovereign, used by all skills & integrations.
    """
    def __init__(self):
        self.lark_app_id = os.getenv("LARK_APP_ID")
        self.lark_app_secret = os.getenv("LARK_APP_SECRET")
        self.redis = memory_store.client

    async def get_lark_token(self) -> str:
        """
        Fetches or refreshes the Lark tenant_access_token.
        """
        if not self.lark_app_id or not self.lark_app_secret:
            logger.warning("[AUTH] Lark Credentials missing in .env")
            return "MOCK_LARK_TOKEN"

        # 1. Check Cache (Redis)
        cache_key = "auth:lark:tenant_access_token"
        if self.redis:
             cached = self.redis.get(cache_key)
             if cached: return cached

        # 2. Refresh Token
        try:
            url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.lark_app_id,
                "app_secret": self.lark_app_secret
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, timeout=10.0)
                if res.status_code == 200:
                    data = res.json()
                    token = data.get("tenant_access_token")
                    expiry = data.get("expire", 7200) - 300 # Buffer 5 mins
                    
                    if token and self.redis:
                        self.redis.set(cache_key, token, ex=expiry)
                        logger.info("[AUTH] Lark Token refreshed and cached.")
                    
                    return token
                else:
                    logger.error(f"[AUTH] Lark Refresh failed: {res.text}")
                    return None
        except Exception as e:
            logger.error(f"[AUTH] Error refreshing Lark token: {e}")
            return None

    async def get_service_auth(self, service_name: str) -> dict:
        """
        Generic helper to get headers or tokens for any authorized service.
        """
        if service_name.lower() == "lark":
            token = await self.get_lark_token()
            return {"Authorization": f"Bearer {token}"} if token else {}
        
        # Future: Add GitHub, Slack, etc.
        return {}

# Singleton
token_manager = TokenManager()
