from qdrant_client import QdrantClient
from qdrant_client.http import models
import os

class QdrantStore:
    def __init__(self, host=None, port=6333):
        self.host = host or os.getenv("QDRANT_HOST", "nex-niflo-agent-qdrant")
        self.client = QdrantClient(host=self.host, port=port)
        
    def ensure_collection(self, collection_name, vector_size):
        try:
            self.client.get_collection(collection_name)
        except:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )
            
    def upsert_document(self, collection_name, point_id, vector, payload):
        """
        Payload MUST contain: source, type, tenant as per architecture mandate.
        """
        required_keys = ["source", "type", "tenant"]
        for key in required_keys:
            if key not in payload:
                payload[key] = "unknown"
                
        self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        
    def search(self, collection_name, query_vector, limit=5, tenant=None):
        search_filter = None
        if tenant:
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="tenant",
                        match=models.MatchValue(value=tenant),
                    )
                ]
            )
            
        # Use modern query_points for better compatibility and filtering
        search_result = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=search_filter,
            limit=limit
        ).points
        
        return search_result

# Singleton instance
vector_store = QdrantStore()
