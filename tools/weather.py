import logging
import requests
from config import OPENWEATHER_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(location: str) -> dict:
    """Fetch current weather for a location and return weather details with a wardrobe tag."""
    try:
        response = requests.get(BASE_URL, params={
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        })
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        conditions = data["weather"][0]["description"]

        if "rain" in conditions:
            weather_tag = "rainy"
        elif temp < 20:
            weather_tag = "cool"
        elif temp < 28:
            weather_tag = "mild"
        else:
            weather_tag = "warm"

        return {
            "temperature": temp,
            "conditions": conditions,
            "humidity": data["main"]["humidity"],
            "weather_tag": weather_tag
        }

    except requests.exceptions.HTTPError as e:
        logger.error(f"Weather API HTTP error: {e}")
        return {"error": f"Location '{location}' not found or API error"}
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return {"error": f"Failed to fetch weather: {str(e)}"}