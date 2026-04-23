import uuid
from memory.long_term import vector_store
from integrations.llm import llm
import os

class RAGVectorStore:
    def __init__(self, collection_name="nex_knowledge"):
        self.collection_name = collection_name
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        # Ensure collection exists on init
        self.vector_size = 1536 if "text-embedding-3" in self.embedding_model else 768
        
    def add_chunks(self, chunks):
        vector_store.ensure_collection(self.collection_name, self.vector_size)
        for chunk in chunks:
            embedding = llm.embed(self.embedding_model, chunk.text)
            if embedding:
                point_id = str(uuid.uuid4())
                payload = chunk.metadata.model_dump()
                payload["text"] = chunk.text
                vector_store.upsert_document(self.collection_name, point_id, embedding, payload)

    def query(self, text, limit=5, tenant="default"):
        embedding = llm.embed(self.embedding_model, text)
        if not embedding:
            return []
            
        results = vector_store.search(self.collection_name, embedding, limit=limit, tenant=tenant)
        return [
            {
                "text": r.payload.get("text"),
                "metadata": {k: v for k, v in r.payload.items() if k != "text"},
                "score": r.score
            }
            for r in results
        ]

# Singleton
rag_store = RAGVectorStore()
