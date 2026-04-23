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
    
    # AI SEARCH PATH (Premium) - Ensure it's not the placeholder
    if api_key and api_key != "tvly-your-key-here":
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
                    timeout=15.0
                )
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "status": "success",
                        "data": data,
                        "message": "Internet search complete via Tavily."
                    }
                else:
                    logger.warning(f"[SKILLS] Tavily API returned {res.status_code}. Falling back.")
        except Exception as e:
            logger.error(f"[SKILLS] Tavily failed: {e}")

    # FREE FALLBACK PATH (DuckDuckGo Scraper style)
    logger.info(f"[SKILLS] Attempting free search fallback for: {query}")
    try:
        async with httpx.AsyncClient() as client:
            # Using the 'lite' DuckDuckGo view which is more stable for scraping
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            res = await client.get(f"https://duckduckgo.com/lite/?q={query}", headers=headers, timeout=10.0)
            
            # More robust parsing for lite version
            # Titles are in <a class="result-link">
            # Snippets are in <td class="result-snippet">
            from html import unescape
            titles = re.findall(r'class="result-link">([\s\S]*?)</a>', res.text)
            snippets = re.findall(r'class="result-snippet">([\s\S]*?)</td>', res.text)
            
            results = []
            for i in range(min(5, len(titles), len(snippets))):
                clean_title = re.sub('<[^<]+?>', '', titles[i])
                clean_snippet = re.sub('<[^<]+?>', '', snippets[i])
                results.append({
                    "title": unescape(clean_title.strip()), 
                    "content": unescape(clean_snippet.strip())
                })

            if not results:
                # If lite fails, try one more time header/meta approach
                return {"status": "error", "message": "Search failed or returned no results. Check internet connection."}

            return {
                "status": "success",
                "data": {"results": results},
                "message": "Internet search complete via DuckDuckGo Fallback."
            }
    except Exception as e:
        logger.error(f"[SKILLS] Web search exception: {e}")
        return {"status": "error", "message": f"Search fallback failed: {str(e)}"}
