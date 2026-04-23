# skills/knowledge/duckduckgo_search.py
import httpx
import logging
import re

logger = logging.getLogger("nex-skills")

async def duckduckgo_search(input_data: dict):
    """
    Search the internet for real-time information using DuckDuckGo (Free).
    Params: query (string)
    """
    query = input_data.get("query")
    if not query:
        return {"status": "error", "message": "No query provided for web search"}

    logger.info(f"[SKILLS] DuckDuckGo Searching: {query}")
    try:
        async with httpx.AsyncClient() as client:
            # We use the DuckDuckGo HTML endpoint (no-js) for easy scraping
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            res = await client.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=10.0)
            
            # Simple regex to extract basic snippets and titles
            snippets = re.findall(r'<a class="result__snippet"[\s\S]*?>(.*?)</a>', res.text)
            titles = re.findall(r'<a class="result__a"[\s\S]*?>(.*?)</a>', res.text)
            
            results = []
            for i in range(min(5, len(snippets))):
                clean_snippet = re.sub('<[^<]+?>', '', snippets[i])
                clean_title = re.sub('<[^<]+?>', '', titles[i])
                results.append({
                    "title": clean_title.strip(),
                    "content": clean_snippet.strip()
                })

            if not results:
                # Try fallback for some localized titles
                return {"status": "error", "message": "DuckDuckGo returned no usable snippets. The service might be rate-limiting."}

            return {
                "status": "success",
                "data": {"results": results},
                "message": "Internet search complete via DuckDuckGo."
            }
    except Exception as e:
        logger.error(f"[SKILLS] DuckDuckGo failed: {e}")
        return {"status": "error", "message": f"DuckDuckGo search failed: {str(e)}"}
