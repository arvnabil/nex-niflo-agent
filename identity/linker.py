import uuid
import logging
import json
from memory.short_term import memory_store

logger = logging.getLogger("nex-identity")

class IdentityLinker:
    """
    Handles Multi-Channel Identity Linking.
    Maps Telegram IDs, Web IDs (LibreChat), etc. to a single internal UUID.
    """
    def __init__(self):
        self.redis = memory_store.client

    def get_internal_id(self, channel: str, channel_id: str) -> str:
        """Resolves a channel-specific ID to an internal UUID."""
        if not self.redis: return f"temp_{channel_id}"
        
        mapping_key = f"identity:{channel}:{channel_id}"
        internal_id = self.redis.get(mapping_key)
        
        if not internal_id:
            logger.info(f"[IDENTITY] New user detected on {channel}:{channel_id}. Creating temporary context.")
            return f"temp_{channel_id}"
        
        return internal_id

    def link_accounts(self, internal_id: str, channel: str, channel_id: str):
        """Links a channel-specific ID to an existing internal UUID."""
        if not self.redis: return False
        
        mapping_key = f"identity:{channel}:{channel_id}"
        self.redis.set(mapping_key, internal_id)
        
        # Also store the reverse mapping to know all channels for a user
        user_channels_key = f"user:{internal_id}:channels"
        channels = self.get_user_channels(internal_id)
        channels[channel] = channel_id
        self.redis.set(user_channels_key, json.dumps(channels))
        
        logger.info(f"[IDENTITY] Linked {channel}:{channel_id} to {internal_id}")
        return True

    def get_user_channels(self, internal_id: str) -> dict:
        if not self.redis: return {}
        data = self.redis.get(f"user:{internal_id}:channels")
        return json.loads(data) if data else {}

    def create_registration_ticket(self, internal_id: str) -> str:
        """Creates a short-lived token for manual linking (e.g., /link <token>)."""
        if not self.redis: return "ERROR"
        token = str(uuid.uuid4())[:8].upper()
        self.redis.set(f"link_ticket:{token}", internal_id, ex=600) # 10 mins
        return token

    def resolve_link_ticket(self, token: str) -> str:
        if not self.redis: return None
        return self.redis.get(f"link_ticket:{token}")

# Singleton
identity_linker = IdentityLinker()
