# BOOKINGTABLE/bot/api/service_type_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from bot.services.crud_vector_schema import VectorCRUD
from typing import Dict, Any, List
from pydantic import BaseModel, field_validator

from bot.services.generate_embeddings import generate_embedding
from dotenv import load_dotenv
import json

load_dotenv()

service_type_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

def get_vector_crud(db: Session = Depends(get_db)):
    return VectorCRUD(db)

# Pydantic models cho ServiceType
class ServiceTypeCreate(BaseModel):
    branch_id: int
    service_name: str
    description: str
    is_active: bool = True
    
    @field_validator("service_name")
    def validate_service_name(cls, value):
        allowed_names = {
            "Dine-In", "Takeaway", "Delivery", "Buffet", "Catering",
            "Private Dining", "Outdoor Seating", "Bar Service"
        }
        if value not in allowed_names:
            raise ValueError(f"service_name must be one of {allowed_names}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "branch_id": 1,
                "service_name": "Dine-In",
                "description": "Dịch vụ ăn tại chỗ với không gian thoải mái",
                "is_active": True
            }
        }

class ServiceTypeUpdate(BaseModel):
    branch_id: int | None = None
    service_name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    
    @field_validator("service_name")
    def validate_service_name(cls, value):
        if value is None:
            return value
        allowed_names = {
            "Dine-In", "Takeaway", "Delivery", "Buffet", "Catering",
            "Private Dining", "Outdoor Seating", "Bar Service"
        }
        if value not in allowed_names:
            raise ValueError(f"service_name must be one of {allowed_names}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "service_name": "Takeaway",
                "description": "Dịch vụ mang đi nhanh chóng"
            }
        }

class ServiceTypeResponse(BaseModel):
    service_id: int
    branch_id: int
    service_name: str

class ServiceTypeGetResponse(BaseModel):
    service_id: int
    branch_id: int
    service_name: str
    description: str
    is_active: bool

class SimilarServiceTypeResponse(BaseModel):
    service_id: int
    service_name: str
    distance: float

# ServiceType endpoints
@service_type_router.post("/create_service_type/", response_model=ServiceTypeResponse, summary="Create a new service type")
async def create_service_type(
    service: ServiceTypeCreate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Create a new service type and its embedding."""
        db_service = public_crud.create_service_type(
            branch_id=service.branch_id,  
            service_name=service.service_name,
            description=service.description,
            is_active=service.is_active
        )

        embedding_text = f"Service: {service.service_name}, description: {service.description}"
        embedding_vector = generate_embedding(embedding_text)
        vector_crud.create_service_type_embedding(
            service_id=db_service.service_id,
            embedding=embedding_vector
        )

        return {
            "service_id": db_service.service_id,
            "branch_id": db_service.branch_id,
            "service_name": db_service.service_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@service_type_router.get("/get_service_type/{service_id}", 
                         response_model=ServiceTypeGetResponse, 
                         summary="Get a service type by ID")
async def get_service_type(
    service_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific service type by its ID."""
    service = public_crud.get_service_type(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service type not found")
    return {
        "service_id": service.service_id,
        "branch_id": service.branch_id,
        "service_name": service.service_name,
        "description": service.description,
        "is_active": service.is_active
    }

@service_type_router.put("/update_service_type/{service_id}", 
                         response_model=ServiceTypeResponse, 
                         summary="Update a service type")
async def update_service_type(
    service_id: int,
    service: ServiceTypeUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Update an existing service type and its embedding."""
        data = {k: v for k, v in service.model_dump().items() if v is not None}
        db_service = public_crud.update_service_type(service_id, data)
        if not db_service:
            raise HTTPException(status_code=404, detail="Service type not found")

        # Cập nhật embedding nếu có thay đổi service_name hoặc description
        if "service_name" in data or "description" in data:
            embedding_text = f"Service: {db_service.service_name}, description: {db_service.description}"
            embedding_vector = generate_embedding(embedding_text)
            existing_embedding = vector_crud.get_service_type_embedding(db_service.service_id)
            if existing_embedding:
                vector_crud.update_service_type_embedding(existing_embedding.embedding_id, embedding_vector)
            else:
                vector_crud.create_service_type_embedding(db_service.service_id, embedding_vector)

        return {
            "service_id": db_service.service_id,
            "branch_id": db_service.branch_id,
            "service_name": db_service.service_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@service_type_router.delete("/delete_service_type/{service_id}", summary="Delete a service type")
async def delete_service_type(
    service_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Delete a service type and its associated embedding."""
        # Xóa service type
        deleted = public_crud.delete_service_type(service_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Service type not found")

        # Xóa embedding (nếu có)
        embedding = vector_crud.get_service_type_embedding(service_id)
        if embedding:
            vector_crud.delete_service_type_embedding(embedding.embedding_id)

        return {"message": f"Service type {service_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@service_type_router.get("/service_type-embeddings/similar/", 
                         response_model=List[SimilarServiceTypeResponse], 
                        summary="Find similar service types by embedding")
async def find_similar_service_types(
    query_embedding: str,
    limit: int = 5,
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    """Find service types with embeddings similar to the provided query vector."""
    try:
        query_vector = json.loads(query_embedding)
        results = vector_crud.find_similar_service_type(query_vector, limit)
        return [{"service_id": r[1].service_id, 
                 "service_name": r[1].service_name, 
                 "distance": r[0].embedding.cosine_distance(query_vector)} 
                for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")