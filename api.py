from fastapi import FastAPI
from tools.recommend import recommend_outfit
from tools.weather import get_weather
from tools.wardrobe import (
    get_wardrobe, get_item_details, add_wardrobe_item,
    delete_wardrobe_item, search_wardrobe_item
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/ui")
def ui(request: Request, location: str = "Pune"):
    outfit = recommend_outfit(location)
    wardrobe = get_wardrobe()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "outfit": outfit,
        "wardrobe": wardrobe,
        "location": location
    })

@app.get("/")
def home():
    return {"message": "FitCheck API is running!"}


@app.get("/wardrobe")
def wardrobe():
    return get_wardrobe()


@app.get("/wardrobe/search")
def search(category: str = None, product_type: str = None,
           product_colour: str = None, occasion: str = None,
           product_material: str = None):
    return search_wardrobe_item(category, product_type,
                                product_colour, occasion, product_material)


@app.get("/wardrobe/{item_id}")
def get_wardrobe_item(item_id: int):
    return get_item_details(item_id)


@app.post("/wardrobe")
def add_item(category: str, product_type: str, product_colour: str,
             product_material: str, product_fit: str, occasion: str,
             weather_suitability: str, product_photo: str = None):
    return add_wardrobe_item(category, product_type, product_colour,
                             product_material, product_fit, occasion,
                             weather_suitability, product_photo)


@app.delete("/wardrobe/{item_id}")
def delete_item(item_id: int):
    return delete_wardrobe_item(item_id)


@app.get("/weather")
def weather(location: str):
    return get_weather(location)


@app.get("/recommend")
def recommend(location: str, occasion: str = None):
    return recommend_outfit(location, occasion)