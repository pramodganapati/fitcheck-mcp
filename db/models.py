from sqlalchemy import Column, Integer, String, Text
from db.database import Base


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    product_type = Column(String(100), nullable=False)
    product_colour = Column(String(50), nullable=False)
    product_material = Column(String(100), nullable=False)
    product_fit = Column(String(50), nullable=False)
    occasion = Column(String(100), nullable=False)
    weather_suitability = Column(String(100), nullable=False)
    product_photo = Column(Text, nullable=True)
    description = Column(Text, nullable=True)