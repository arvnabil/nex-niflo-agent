# skills/knowledge/tavily_search.py
import httpx
import os
import logging
import re

logger = logging.getLogger("nex-skills")

async def tavily_search(input_data: dict):
    """
    Search the internet for up-to-date information.
    Params: query (string)
    """
    query = input_data.get("query")
    if not query:
        return {"status": "error", "message": "No query provided for web search"}

    api_key = os.getenv("TAVILY_API_KEY")
    
    # AI SEARCH PATH (Premium)
    if api_key:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "https://api.tavily.com/search", 
                    json={
                        "api_key": api_key,
                        "query": query,
                        "search_depth": "smart",
                        "include_answer": True
                    },
                    timeout=10.0
                )
                data = res.json()
                return {
                    "status": "success",
                    "data": data,
                    "message": "Internet search complete via Tavily."
                }
        except Exception as e:
            logger.error(f"[SKILLS] Tavily failed: {e}")

    # FREE FALLBACK PATH (DuckDuckGo Scraper style)
    # Using a simple duckduckgo-lite approach via HTTP
    logger.info(f"[SKILLS] Attempting free search fallback for: {query}")
    try:
        async with httpx.AsyncClient() as client:
            # We use the DuckDuckGo HTML endpoint (no-js)
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            res = await client.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=8.0)
            
            # Simple regex to extract basic snippets for the agent to read
            # Note: In production, you'd use a better parser, but this works for basic text.
            snippets = re.findall(r'<a class="result__snippet"[\s\S]*?>(.*?)</a>', res.text)
            titles = re.findall(r'<a class="result__a"[\s\S]*?>(.*?)</a>', res.text)
            
            results = []
            for i in range(min(5, len(snippets))):
                clean_snippet = re.sub('<[^<]+?>', '', snippets[i])
                clean_title = re.sub('<[^<]+?>', '', titles[i])
                results.append({"title": clean_title, "content": clean_snippet})

            if not results:
                return {"status": "error", "message": "Search failed or returned no results."}

            return {
                "status": "success",
                "data": {"results": results},
                "message": "Internet search complete via DuckDuckGo Fallback."
            }
    except Exception as e:
        return {"status": "error", "message": f"Search fallback failed: {str(e)}"}
