# 🪡 FitCheck — AI-Powered Personal Stylist

✨ FitCheck is an MCP (Model Context Protocol) server that connects Claude Desktop to your personal wardrobe database. Ask Claude naturally — it checks live weather, picks weather-appropriate clothes from your wardrobe, and uses Gemini AI to recommend the best matching outfit with a style score and reasoning.

---

## 🏗️ Architecture
```
Claude Desktop
      |
   MCP Server
      |
  -------------------------
  |           |           |
PostgreSQL  OpenWeatherMap  Gemini API
(wardrobe)  (weather)      (vision + reasoning)
```

---

## ⚙️ How It Works

1. You ask Claude — *"Recommend a casual outfit for Pune today"*
2. `get_weather()` fetches live weather → maps to tag (warm / mild / cool / rainy)
3. Wardrobe items matching weather + occasion fetched from PostgreSQL
4. Items and style descriptions sent to Gemini
5. Gemini picks best top + bottom + footwear combo
6. Returns match score (1-10), verdict, and style reasoning
7. Outerwear added automatically for cool or rainy weather

You can also add items by photo — Gemini Vision auto-detects colour, type, fit, occasion, and generates a style description.

---

## 🛠️ Tech Stack

- Python MCP SDK (FastMCP)
- PostgreSQL 18 + SQLAlchemy ORM
- OpenWeatherMap API (free tier)
- Google Gemini 2.5 Flash (vision + outfit reasoning)

---

## 📋 Requirements

- Python 3.10+
- PostgreSQL 18
- Claude Desktop
- OpenWeatherMap API key — https://openweathermap.org/api
- Google Gemini API key — https://aistudio.google.com/apikey

---

## 🚀 Setup
```bash
git clone https://github.com/pramodganapati/fitcheck-mcp.git
cd fitcheck-mcp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in project root:
```env
DB_URL=postgresql://postgres:PASSWORD@localhost:PORT/fitcheck
OPENWEATHER_API_KEY=your_key
GEMINI_API_KEY=your_key
```

Create a PostgreSQL database named `fitcheck`, then run `python server.py` once to auto-create tables.

Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "fitcheck": {
      "command": "C:\\path\\to\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\server.py"],
      "env": { "PYTHONPATH": "C:\\path\\to\\fitcheck-mcp" }
    }
  }
}
```

Restart Claude Desktop — a hammer icon in the chat bar confirms the server is connected.