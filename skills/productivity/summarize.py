# skills/productivity/summarize.py

async def summarize(input_data: dict):
    """
    Summarizes long text into key insights.
    Params: text (string)
    """
    text = input_data.get("text")

    if not text:
        return {"status": "error", "message": "No text provided to summarize"}

    # Placeholder for actual LLM summarization logic
    # In a real scenario, this would call another internal agent or an LLM service
    summary = text[:300] + "..." if len(text) > 300 else text

    return {
        "status": "success",
        "data": {"summary": summary},
        "message": "Text successfully summarized."
    }
