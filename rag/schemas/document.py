from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class DocumentMetadata(BaseModel):
    source: str
    type: str
    tenant: str
    page: Optional[int] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

class DocumentChunk(BaseModel):
    text: str
    metadata: DocumentMetadata
