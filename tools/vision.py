import json
import logging
import shutil
from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

IMAGES_DIR = Path("C:/FitCheck/images")
IMAGES_DIR.mkdir(exist_ok=True)


def analyse_clothing_image(image_path: str) -> dict:
    """Send image to Gemini Vision and extract clothing attributes."""
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()

        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }
        mime_type = mime_types.get(ext, "image/jpeg")

        prompt = """Analyse this clothing item and return ONLY a JSON object with these exact fields:
{
    "category": one of [top, bottom, footwear, accessory, outerwear],
    "product_type": e.g. shirt, jeans, sneakers,
    "product_colour": main colour,
    "product_fit": one of [regular, slim, oversized, relaxed],
    "occasion": one of [casual, formal, party, sports],
    "weather_suitability": one of [warm, cool, mild, rainy, all],
    "description": a natural language description of the item for style matching
}
Return ONLY the JSON object, no explanation, no markdown."""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                types.Part.from_bytes(data=image_data, mime_type=mime_type),
                prompt
            ]
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        attributes = json.loads(raw.strip())
        return {"success": True, "attributes": attributes}

    except json.JSONDecodeError:
        logger.error("Gemini returned invalid JSON")
        return {"success": False, "error": "Could not parse clothing attributes"}
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        return {"success": False, "error": str(e)}


def save_image_locally(source_path: str, item_name: str) -> str:
    """Copy image to FitCheck images folder and return new path."""
    try:
        source = Path(source_path)
        if source.parent.resolve() == IMAGES_DIR.resolve():
            return source_path
        
        ext = source.suffix
        filename = f"{item_name.replace(' ', '_')}{ext}"
        dest_path = IMAGES_DIR / filename
        shutil.copy2(source_path, dest_path)
        return str(dest_path)
    except Exception as e:
        logger.error(f"Image save failed: {e}")
        return source_path