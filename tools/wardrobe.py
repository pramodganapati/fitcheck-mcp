import logging
from db.database import SessionLocal
from db.models import WardrobeItem
from tools.vision import analyse_clothing_image, save_image_locally

logger = logging.getLogger(__name__)

VALID_CATEGORIES = ["top", "bottom", "footwear", "accessory", "outerwear"]
VALID_OCCASIONS = ["casual", "formal", "party", "sports"]
VALID_WEATHER = ["warm", "cool", "mild", "rainy", "all"]

def get_wardrobe():
    try:
        db = SessionLocal()
        items = db.query(WardrobeItem).all()
        if not items:
            return []
        return [
            {
                "id": item.id,
                "category": item.category,
                "product_type": item.product_type,
                "product_colour": item.product_colour,
                "product_material": item.product_material,
                "product_fit": item.product_fit,
                "occasion": item.occasion,
                "weather_suitability": item.weather_suitability,
                "product_photo": item.product_photo,
                "description": item.description
            }
            for item in items
        ]
    except Exception as e:
        logger.error(f"Error fetching wardrobe: {e}")
        return []
    finally:
        db.close()


def add_wardrobe_item(category: str, product_type: str, product_colour: str,
                      product_material: str, product_fit: str, occasion: str,
                      weather_suitability: str, product_photo: str = None, description: str = None):
    try:
        category = category.lower()
        occasion = occasion.lower()
        weather_suitability = weather_suitability.lower()

        if category not in VALID_CATEGORIES:
            return f"Invalid category '{category}'. Must be one of: {VALID_CATEGORIES}"

        if occasion not in VALID_OCCASIONS:
            return f"Invalid occasion '{occasion}'. Must be one of: {VALID_OCCASIONS}"

        if weather_suitability not in VALID_WEATHER:
            return f"Invalid weather '{weather_suitability}'. Must be one of: {VALID_WEATHER}"

        db = SessionLocal()
        item = WardrobeItem(
            category=category,
            product_type=product_type,
            product_colour=product_colour,
            product_material=product_material,
            product_fit=product_fit,
            occasion=occasion,
            weather_suitability=weather_suitability,
            product_photo=product_photo,
            description=description
        )
        db.add(item)
        db.commit()
        return f"Successfully added {product_colour} {product_type} to wardrobe!"
    except Exception as e:
        logger.error(f"Error adding wardrobe item: {e}")
        return f"Failed to add item: {str(e)}"
    finally:
        db.close()


def delete_wardrobe_item(item_id: int):
    try:
        db = SessionLocal()
        item = db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()
        if not item:
            return f"No item found with id {item_id}"
        db.delete(item)
        db.commit()
        return f"Successfully deleted item {item_id}"
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return f"Failed to delete item: {str(e)}"
    finally:
        db.close()


def get_item_details(item_id: int):
    try:
        db = SessionLocal()
        item = db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()
        if not item:
            return f"No item found with id {item_id}"
        return {
            "id": item.id,
            "category": item.category,
            "product_type": item.product_type,
            "product_colour": item.product_colour,
            "product_material": item.product_material,
            "product_fit": item.product_fit,
            "occasion": item.occasion,
            "weather_suitability": item.weather_suitability,
            "product_photo": item.product_photo,
            "description": item.description
        }
    except Exception as e:
        logger.error(f"Error fetching item: {e}")
        return f"Failed to fetch item: {str(e)}"
    finally:
        db.close()


def search_wardrobe_item(category: str = None, product_type: str = None,
                          product_colour: str = None, occasion: str = None,
                          product_material: str = None):
    try:
        db = SessionLocal()
        query = db.query(WardrobeItem)

        if category:
            query = query.filter(WardrobeItem.category.ilike(f"%{category}%"))
        if product_type:
            query = query.filter(WardrobeItem.product_type.ilike(f"%{product_type}%"))
        if product_colour:
            query = query.filter(WardrobeItem.product_colour.ilike(f"%{product_colour}%"))
        if occasion:
            query = query.filter(WardrobeItem.occasion.ilike(f"%{occasion}%"))
        if product_material:
            query = query.filter(WardrobeItem.product_material.ilike(f"%{product_material}%"))

        items = query.all()

        if not items:
            return "No matching items found"

        return [
            {
                "id": item.id,
                "category": item.category,
                "product_type": item.product_type,
                "product_colour": item.product_colour,
                "occasion": item.occasion,
                "description": item.description
            }
            for item in items
        ]
    except Exception as e:
        logger.error(f"Error searching wardrobe: {e}")
        return f"Search failed: {str(e)}"
    finally:
        db.close()



def add_item_from_image(image_path: str, material: str = None) -> str:
    """Analyse a clothing image and add it to the wardrobe."""
    try:
        result = analyse_clothing_image(image_path)
        
        if not result["success"]:
            return f"Image analysis failed: {result['error']}"
        
        attrs = result["attributes"]
        
        saved_path = save_image_locally(
            image_path,
            f"{attrs['product_colour']}_{attrs['product_type']}"
        )
        
        return add_wardrobe_item(
            category=attrs["category"],
            product_type=attrs["product_type"],
            product_colour=attrs["product_colour"],
            product_material=material or "unknown",
            product_fit=attrs["product_fit"],
            occasion=attrs["occasion"],
            weather_suitability=attrs["weather_suitability"],
            product_photo=saved_path,
            description=attrs["description"]
        )

    except Exception as e:
        logger.error(f"add_item_from_image failed: {e}")
        return f"Failed to add item from image: {str(e)}"