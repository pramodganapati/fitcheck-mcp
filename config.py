import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not DB_URL:
    raise ValueError("DB_URL is not set in .env file")

if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY is not set in .env file")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env file")