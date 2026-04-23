# skills/knowledge/rag_search.py
from rag.vectorstore.qdrant import rag_store

async def rag_search(input_data: dict):
    """
    Searches local knowledge base for relevant context.
    Params: query (string), tenant (string)
    """
    query = input_data.get("query")
    tenant = input_data.get("tenant", "default")

    if not query:
        return {"status": "error", "message": "No query provided for RAG search"}

    try:
        results = rag_store.query(query, limit=5, tenant=tenant)
        if not results:
            return {
                "status": "no_context", 
                "message": "No relevant information found in the local knowledge base."
            }
        
        context = "\n---\n".join([r["text"] for r in results])
        return {
            "status": "success",
            "data": results,
            "message": f"Found context:\n{context}"
        }
    except Exception as e:
        return {"status": "error", "message": f"RAG Search failed: {str(e)}"}
