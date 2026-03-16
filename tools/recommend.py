import random
import logging
from sqlalchemy import or_
from tools.weather import get_weather
from db.database import SessionLocal
from db.models import WardrobeItem
import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

logger = logging.getLogger(__name__)


def _item_to_dict(item: WardrobeItem) -> dict:
    """Convert a WardrobeItem to a readable dictionary."""
    return {
        "id": item.id,
        "type": item.product_type,
        "colour": item.product_colour,
        "material": item.product_material,
        "occasion": item.occasion
    }



def recommend_outfit(location: str, occasion: str = None) -> dict:
    """Recommend a weather-appropriate outfit for a given location and occasion."""
    try:
        weather = get_weather(location)
        if "error" in weather:
            return {"error": weather["error"]}

        keyword = weather["weather_tag"]

        db = SessionLocal()
        clothes = db.query(WardrobeItem).filter(
            or_(
                WardrobeItem.weather_suitability.ilike(f"%{keyword}%"),
                WardrobeItem.weather_suitability.ilike("%all%")
            )
        ).all()
        db.close()

        if occasion:
            clothes = [c for c in clothes if c.occasion == occasion.lower()]

        tops      = [c for c in clothes if c.category == "top"]
        bottoms   = [c for c in clothes if c.category == "bottom"]
        footwear  = [c for c in clothes if c.category == "footwear"]
        outerwear = [c for c in clothes if c.category == "outerwear"]

        # ── Legitimate no match ───────────────────────────────────────────────
        if not tops or not bottoms or not footwear:
            missing = [cat for cat, lst in [("top", tops), ("bottom", bottoms), ("footwear", footwear)] if not lst]
            return {
                "error": f"No suitable clothes found for '{keyword}' weather"
                         + (f" ({occasion} occasion)" if occasion else ""),
                "missing_categories": missing
            }

        # ── Gemini picks best combo from filtered items ───────────────────────
        match_result = _check_outfit_match(tops, bottoms, footwear)

        if match_result:
            # Map chosen ids back to WardrobeItem objects
            top_map      = {t.id: t for t in tops}
            bottom_map   = {b.id: b for b in bottoms}
            footwear_map = {f.id: f for f in footwear}

            chosen_top      = top_map.get(match_result["top_id"])
            chosen_bottom   = bottom_map.get(match_result["bottom_id"])
            chosen_footwear = footwear_map.get(match_result["footwear_id"])

            # Safety — if Gemini returns an id outside filtered list, fallback
            if not all([chosen_top, chosen_bottom, chosen_footwear]):
                logger.warning("Gemini returned id outside filtered set, falling back to random")
                chosen_top      = random.choice(tops)
                chosen_bottom   = random.choice(bottoms)
                chosen_footwear = random.choice(footwear)
                match_result    = None

        else:
            # Gemini call failed entirely — fallback to random
            chosen_top      = random.choice(tops)
            chosen_bottom   = random.choice(bottoms)
            chosen_footwear = random.choice(footwear)

        chosen_outerwear = random.choice(outerwear) if outerwear and keyword in ["cool", "rainy"] else None

        return {
            "weather": {"location": location, "condition": keyword},
            "outfit": {
                "top":       _item_to_dict(chosen_top),
                "bottom":    _item_to_dict(chosen_bottom),
                "footwear":  _item_to_dict(chosen_footwear),
                "outerwear": _item_to_dict(chosen_outerwear) if chosen_outerwear else None,
            },
            "match_result": match_result or {"verdict": "fallback", "reason": "Gemini unavailable, random pick used"}
        }

    except Exception as e:
        logger.error(f"Outfit recommendation failed: {e}")
        return {"error": f"Failed to recommend outfit: {str(e)}"}


# ─────────────────────────────────────────
# INTERNAL HELPER — not an MCP tool
# ─────────────────────────────────────────

def _check_outfit_match(
    tops: list[WardrobeItem],
    bottoms: list[WardrobeItem],
    footwear: list[WardrobeItem]
) -> dict:
    """
    Passes all filtered items to Gemini and lets it pick the best combo.
    Returns chosen ids + match details.
    """
    try:
        def fmt(items):
            return [
                {
                    "id": item.id,
                    "type": item.product_type,
                    "colour": item.product_colour,
                    "fit": item.product_fit,
                    "occasion": item.occasion,
                    "description": item.description or f"{item.product_colour} {item.product_type}"
                }
                for item in items
            ]

        prompt = f"""You are a fashion expert. From the available clothing items below, pick the BEST matching outfit combination.

        Available Tops:
        {json.dumps(fmt(tops), indent=2)}

        Available Bottoms:
        {json.dumps(fmt(bottoms), indent=2)}

        Available Footwear:
        {json.dumps(fmt(footwear), indent=2)}

        Return ONLY a JSON object:
        {{
            "top_id": <id of chosen top>,
            "bottom_id": <id of chosen bottom>,
            "footwear_id": <id of chosen footwear>,
            "match_score": <number from 1-10>,
            "verdict": "great match" or "decent match" or "poor match",
            "reason": "<one sentence explaining the combination>",
            "suggestion": "<one improvement tip if score < 7, else null>"
        }}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw.strip())

    except Exception as e:
        logger.error(f"Gemini outfit match failed: {e}")
        return None  # caller handles fallback