# BOOKINGTABLE/bot/api/restaurant_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from bot.services.crud_vector_schema import VectorCRUD
from typing import List
from pydantic import BaseModel
import json

from bot.services.generate_embeddings import generate_embedding
from dotenv import load_dotenv

load_dotenv()

restaurant_router = APIRouter()

# Request/response for restaurant 
class RestaurantCreate(BaseModel):
    name: str
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lửa & Lá",
                "description": """Lửa & Lá là nhà hàng ẩm thực fusion độc đáo kết hợp giữa hương vị truyền thống Việt Nam và phong cách hiện đại phương Tây. 
                Với không gian ấm cúng, thực đơn sáng tạo và nguyên liệu hữu cơ, nhà hàng mang đến trải nghiệm ẩm thực tinh tế và đầy cảm hứng cho mọi thực khách"""
            }
        }
        
class RestaurantUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lửa & Lá",
                "description": "description updated."
            }
        }

class RestaurantResponse(BaseModel):
    restaurant_id: int
    name: str
    
class RestaurantGetResponse(BaseModel):
    restaurant_id: int
    name: str
    description: str
    
class SimilarRestaurantResponse(BaseModel):
    restaurant_id: int
    name: str
    distance: float

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

def get_vector_crud(db: Session = Depends(get_db)):
    return VectorCRUD(db)

# Restaurant endpoints
@restaurant_router.post("/create_restaurants/", response_model=RestaurantResponse, summary="Create a new restaurant")
async def create_restaurant(
    restaurant: RestaurantCreate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud : VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Create a new restaurant and embedding restaurant in the system."""
        db_restaurant = public_crud.create_restaurant(
            name=restaurant.name,
            description=restaurant.description
        )

        embedding_text = f"Name: {restaurant.name}, description: {restaurant.description}"
        embedding_vector = generate_embedding(embedding_text)

        vector_crud.create_restaurant_embedding(
            restaurant_id = db_restaurant.restaurant_id,
            embedding = embedding_vector
        )
        
        return {"restaurant_id": db_restaurant.restaurant_id, "name": db_restaurant.name}
    except Exception as e:
        raise f'Server error: {e}'

@restaurant_router.get("/get_restaurants/{restaurant_id}", 
                       response_model=RestaurantGetResponse, 
                       summary="Get a restaurant by ID")
async def get_restaurant(restaurant_id: int, crud: PublicCRUD = Depends(get_public_crud)):
    """Retrieve details of a specific restaurant by its ID."""
    restaurant = crud.get_restaurant(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return {
        "restaurant_id": restaurant.restaurant_id, 
        "name": restaurant.name, 
        "description": restaurant.description
    }

@restaurant_router.put("/update_restaurants/{restaurant_id}", response_model=RestaurantResponse, summary="Update a restaurant")
async def update_restaurant(
    restaurant_id: int,
    restaurant: RestaurantUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Update an existing restaurant and its embedding."""
        data = {k: v for k, v in restaurant.model_dump().items() if v is not None} 
        db_restaurant = public_crud.update_restaurant(restaurant_id, data)
        if not db_restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        if data.get("name") or data.get("description"):
            embedding_text = f"Name: {db_restaurant.name}, description: {db_restaurant.description}"
            embedding_vector = generate_embedding(embedding_text)
            existing_embedding = vector_crud.get_restaurant_embedding(db_restaurant.restaurant_id)
            if existing_embedding:
                vector_crud.update_restaurant_embedding(existing_embedding.embedding_id, embedding_vector)
            else:
                vector_crud.create_restaurant_embedding(db_restaurant.restaurant_id, embedding_vector)

        return {"restaurant_id": db_restaurant.restaurant_id, "name": db_restaurant.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
    
@restaurant_router.delete("/delete_restaurants/{restaurant_id}", summary="Delete a restaurant")
async def delete_restaurant(
    restaurant_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Delete a restaurant and its associated embedding."""
        deleted = public_crud.delete_restaurant(restaurant_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        return {"message": f"Restaurant deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@restaurant_router.get("/restaurant-embeddings/similar/", response_model=List[SimilarRestaurantResponse], 
           summary="Find similar restaurants by embedding")
async def find_similar_restaurants(
    query_embedding: str,
    limit: int = 5,
    crud: VectorCRUD = Depends(get_vector_crud)
):
    """Find restaurants with embeddings similar to the provided query vector."""
    query_vector = json.loads(query_embedding)
    results = crud.find_similar_restaurants(query_vector, limit)
    return [{"restaurant_id": r[1].restaurant_id, 
             "name": r[1].name, 
             "distance": r[0].embedding.cosine_distance(query_vector)} 
            for r in results]