# skills/knowledge/weather_check.py
import httpx
import logging

logger = logging.getLogger("nex-skills")

async def weather_check(input_data: dict):
    """
    Check current weather and temperature for a given city.
    Params: city (string)
    """
    city = input_data.get("city", "Jakarta")
    logger.info(f"[SKILLS] Checking weather for: {city}")
    
    try:
        async with httpx.AsyncClient() as client:
            # We use wttr.in which is a great free weather API
            # Filtering for English/Indonesian style results
            url = f"https://wttr.in/{city}?format=j1"
            res = await client.get(url, timeout=10.0)
            
            if res.status_code != 200:
                return {"status": "error", "message": f"Could not fetch weather for '{city}'. Location might be unknown."}
            
            data = res.json()
            current = data['current_condition'][0]
            temp = current['temp_C']
            # Get the description (preferring translated if available, else default)
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            feels_like = current['FeelsLikeC']
            
            # Formulating a clean Indonesian overview for the agent to use
            report = f"Cuaca di {city}: {desc}. Suhu: {temp}°C (Terasa seperti {feels_like}°C). Kelembapan: {humidity}%."
            
            return {
                "status": "success",
                "data": {
                    "city": city,
                    "temp": temp,
                    "desc": desc,
                    "humidity": humidity,
                    "feels_like": feels_like
                },
                "message": report
            }
    except Exception as e:
        logger.error(f"[SKILLS] Weather check exception: {e}")
        return {"status": "error", "message": f"Weather service is temporarily down or invalid location: {str(e)}"}
