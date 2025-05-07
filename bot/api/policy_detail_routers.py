# BOOKINGTABLE/bot/api/policy_detail_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from bot.services.crud_vector_schema import VectorCRUD
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from bot.services.generate_embeddings import generate_embedding
import json

policy_detail_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

def get_vector_crud(db: Session = Depends(get_db)):
    return VectorCRUD(db)

# Pydantic models cho PolicyDetail
class PolicyDetailCreate(BaseModel):
    policy_id: int
    details: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": 1,
                "details": {
                    "max_hours": 2,
                    "fee": "10 USD"
                }
            }
        }

class PolicyDetailUpdate(BaseModel):
    policy_id: int | None = None
    details: Dict[str, Any] | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "details": {
                    "max_hours": 3,
                    "fee": "15 USD"
                }
            }
        }

class PolicyDetailResponse(BaseModel):
    detail_id: int
    policy_id: int
    details: Dict[str, Any]

class PolicyDetailGetResponse(BaseModel):
    detail_id: int
    policy_id: int
    details: Dict[str, Any]
    created_at: datetime

class SimilarPolicyDetailResponse(BaseModel):
    detail_id: int
    details: Dict[str, Any]
    distance: float

# PolicyDetail endpoints
@policy_detail_router.post("/create_policy_detail/", 
                           response_model=PolicyDetailResponse, 
                           summary="Create a new policy detail")
async def create_policy_detail(
    policy_detail: PolicyDetailCreate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Create a new policy detail and its embedding."""
        db_policy_detail = public_crud.create_policy_details(
            policy_id=policy_detail.policy_id,
            details=policy_detail.details
        )

        embedding_text = json.dumps(policy_detail.details)  # Chuyển details thành chuỗi JSON để tạo embedding
        embedding_vector = generate_embedding(embedding_text)
        vector_crud.create_policy_details_embedding(
            policy_detail_id=db_policy_detail.detail_id,
            embedding=embedding_vector
        )

        return {
            "detail_id": db_policy_detail.detail_id,
            "policy_id": db_policy_detail.policy_id,
            "details": db_policy_detail.details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_detail_router.get("/get_policy_detail/{detail_id}", 
                          response_model=PolicyDetailGetResponse, 
                          summary="Get a policy detail by ID")
async def get_policy_detail(
    detail_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific policy detail by its ID."""
    policy_detail = public_crud.get_policy_details(detail_id)
    if not policy_detail:
        raise HTTPException(status_code=404, detail="Policy detail not found")
    return {
        "detail_id": policy_detail.detail_id,
        "policy_id": policy_detail.policy_id,
        "details": policy_detail.details,
        "created_at": policy_detail.created_at
    }

@policy_detail_router.put("/update_policy_detail/{detail_id}", 
                          response_model=PolicyDetailResponse, 
                          summary="Update a policy detail")
async def update_policy_detail(
    detail_id: int,
    policy_detail: PolicyDetailUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Update an existing policy detail and its embedding."""
        data = {k: v for k, v in policy_detail.model_dump().items() if v is not None}
        db_policy_detail = public_crud.update_policy_details(detail_id, data)
        if not db_policy_detail:
            raise HTTPException(status_code=404, detail="Policy detail not found")

        if "details" in data:
            embedding_text = json.dumps(db_policy_detail.details)
            embedding_vector = generate_embedding(embedding_text)
            existing_embedding = vector_crud.get_policy_details_embedding(db_policy_detail.detail_id)  # Lấy bằng detail_id
            if existing_embedding:
                vector_crud.update_policy_details_embedding(existing_embedding.embedding_id, embedding_vector)
            else:
                vector_crud.create_policy_details_embedding(db_policy_detail.detail_id, embedding_vector)

        return {
            "detail_id": db_policy_detail.detail_id,
            "policy_id": db_policy_detail.policy_id,
            "details": db_policy_detail.details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_detail_router.delete("/delete_policy_detail/{detail_id}", summary="Delete a policy detail")
async def delete_policy_detail(
    detail_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Delete a policy detail and its associated embedding."""
        deleted = public_crud.delete_policy_details(detail_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Policy detail not found")

        return {"message": f"Policy detail deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_detail_router.get("/policy_detail-embeddings/similar/", response_model=List[SimilarPolicyDetailResponse], 
                         summary="Find similar policy details by embedding")
async def find_similar_policy_details(
    query_embedding: str,
    limit: int = 5,
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    """Find policy details with embeddings similar to the provided query vector."""
    try:
        query_vector = json.loads(query_embedding)
        results = vector_crud.find_similar_policy_details(query_vector, limit)
        return [{"detail_id": r[1].detail_id, 
                 "details": r[1].details, 
                 "distance": r[0].embedding.cosine_distance(query_vector)} 
                for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")