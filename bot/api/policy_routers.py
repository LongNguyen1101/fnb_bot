# BOOKINGTABLE/bot/api/policy_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from bot.services.crud_vector_schema import VectorCRUD
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

from bot.services.generate_embeddings import generate_embedding
from dotenv import load_dotenv
import json

load_dotenv()

policy_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

def get_vector_crud(db: Session = Depends(get_db)):
    return VectorCRUD(db)

# Pydantic models cho Policy
class PolicyCreate(BaseModel):
    policy_type_id: int
    branch_id: int
    name: str
    is_active: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "policy_type_id": 1,
                "branch_id": 1,
                "name": "Cancellation Fee",
                "is_active": True
            }
        }

class PolicyUpdate(BaseModel):
    policy_type_id: int | None = None
    branch_id: int | None = None
    name: str | None = None
    is_active: bool | None = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Cancellation Fee",
                "is_active": False
            }
        }

class PolicyResponse(BaseModel):
    policy_id: int
    policy_type_id: int
    branch_id: int
    name: str

class PolicyGetResponse(BaseModel):
    policy_id: int
    policy_type_id: int
    branch_id: int
    name: str
    is_active: bool
    created_at: datetime

class SimilarPolicyResponse(BaseModel):
    policy_id: int
    name: str
    distance: float

# Policy endpoints
@policy_router.post("/create_policy/", response_model=PolicyResponse, summary="Create a new policy")
async def create_policy(
    policy: PolicyCreate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Create a new policy and its embedding."""
        db_policy = public_crud.create_policy(
            policy_type_id=policy.policy_type_id,
            branch_id=policy.branch_id,
            name=policy.name
        )

        embedding_text = f"Policy: {policy.name}, is_active: {policy.is_active}"
        embedding_vector = generate_embedding(embedding_text)
        vector_crud.create_policy_embedding(
            policy_id=db_policy.policy_id,
            embedding=embedding_vector
        )

        return {
            "policy_id": db_policy.policy_id,
            "policy_type_id": db_policy.policy_type_id,
            "branch_id": db_policy.branch_id,
            "name": db_policy.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_router.get("/get_policy/{policy_id}", response_model=PolicyGetResponse, summary="Get a policy by ID")
async def get_policy(
    policy_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific policy by its ID."""
    policy = public_crud.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {
        "policy_id": policy.policy_id,
        "policy_type_id": policy.policy_type_id,
        "branch_id": policy.branch_id,
        "name": policy.name,
        "is_active": policy.is_active,
        "created_at": policy.created_at
    }

@policy_router.put("/update_policy/{policy_id}", response_model=PolicyResponse, summary="Update a policy")
async def update_policy(
    policy_id: int,
    policy: PolicyUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Update an existing policy and its embedding."""
        data = {k: v for k, v in policy.model_dump().items() if v is not None}
        db_policy = public_crud.update_policy(policy_id, data)
        if not db_policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        if "name" in data:
            embedding_text = f"Policy: {db_policy.name}"
            embedding_vector = generate_embedding(embedding_text)
            existing_embedding = vector_crud.get_policy_embedding(db_policy.policy_id)  # Sửa để lấy bằng policy_id
            if existing_embedding:
                vector_crud.update_policy_embedding(existing_embedding.embedding_id, embedding_vector)
            else:
                vector_crud.create_policy_embedding(db_policy.policy_id, embedding_vector)

        return {
            "policy_id": db_policy.policy_id,
            "policy_type_id": db_policy.policy_type_id,
            "branch_id": db_policy.branch_id,
            "name": db_policy.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_router.delete("/delete_policy/{policy_id}", summary="Delete a policy")
async def delete_policy(
    policy_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud),
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    try:
        """Delete a policy and its associated embedding."""
        deleted = public_crud.delete_policy(policy_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Policy not found")

        return {"message": f"Policy deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_router.get("/policy-embeddings/similar/", response_model=List[SimilarPolicyResponse], 
                        summary="Find similar policies by embedding")
async def find_similar_policies(
    query_embedding: str,
    limit: int = 5,
    vector_crud: VectorCRUD = Depends(get_vector_crud)
):
    """Find policies with embeddings similar to the provided query vector."""
    try:
        query_vector = json.loads(query_embedding)
        results = vector_crud.find_similar_policy(query_vector, limit)
        return [{"policy_id": r[1].policy_id, 
                 "name": r[1].name, 
                 "distance": r[0].embedding.cosine_distance(query_vector)} 
                for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")