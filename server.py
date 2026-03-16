from mcp.server.fastmcp import FastMCP
from db.database import Base, engine
from db import models
from tools.weather import get_weather as fetch_weather
from tools.wardrobe import (
    get_wardrobe as fetch_wardrobe,
    add_wardrobe_item as save_wardrobe_item,
    delete_wardrobe_item as delete_item,
    get_item_details as get_item,
    search_wardrobe_item as search_item
)
from tools.recommend import recommend_outfit as fetch_outfit
from tools.wardrobe import add_item_from_image as save_item_from_image


# Create tables in PostgreSQL on startup
Base.metadata.create_all(bind=engine)

mcp = FastMCP("FitCheck")


@mcp.tool()
def ping() -> str:
    """Health check — confirms FitCheck MCP server is running."""
    return "FitCheck MCP server is alive!"


@mcp.tool()
def get_weather(location: str) -> dict:
    """Get current weather for a given location."""
    return fetch_weather(location)


@mcp.tool()
def get_wardrobe() -> list:
    """Get all items in the wardrobe."""
    return fetch_wardrobe()


@mcp.tool()
def add_wardrobe_item(category: str, product_type: str, product_colour: str,
                      product_material: str, product_fit: str, occasion: str,
                      weather_suitability: str, product_photo: str = None, description: str = None) -> str:
    """Add a new clothing item to the wardrobe."""
    return save_wardrobe_item(category, product_type, product_colour,
                              product_material, product_fit, occasion,
                              weather_suitability, product_photo,description)


@mcp.tool()
def recommend_outfit(location: str, occasion: str = None) -> dict:
    """Recommend a weather-appropriate outfit for a given location and optional occasion."""
    return fetch_outfit(location, occasion)


@mcp.tool()
def delete_wardrobe_item(item_id: int) -> str:
    """Delete a wardrobe item by its ID."""
    return delete_item(item_id)


@mcp.tool()
def get_item_details(item_id: int) -> dict:
    """Get full details of a wardrobe item by its ID."""
    return get_item(item_id)


@mcp.tool()
def search_wardrobe_item(category: str = None, product_type: str = None,
                          product_colour: str = None, occasion: str = None,
                          product_material: str = None) -> list:
    """Search wardrobe items by any combination of filters."""
    return search_item(category, product_type, product_colour,
                       occasion, product_material)



@mcp.tool()
def add_item_from_image(image_path: str, material: str = None) -> str:
    """Analyse a clothing image using AI and automatically add it to the wardrobe."""
    return save_item_from_image(image_path, material)


if __name__ == "__main__":
    mcp.run(transport="stdio")
