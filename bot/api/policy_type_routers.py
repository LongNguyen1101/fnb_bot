# BOOKINGTABLE/bot/api/policy_type_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from typing import Dict, Any
from pydantic import BaseModel, field_validator
from datetime import datetime

policy_type_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

# Pydantic models cho PolicyType
class PolicyTypeCreate(BaseModel):
    type_name: str
    description: str | None = None
    
    @field_validator("type_name")
    def validate_type_name(cls, value):
        allowed_types = {
            "Cancellation", "Deposit", "Dress Code", "Late Arrival", "No Show",
            "Reservation Time Limit", "Minimum Spend", "Group Size"
        }
        if value not in allowed_types:
            raise ValueError(f"type_name must be one of {allowed_types}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "type_name": "Cancellation",
                "description": "Chính sách hủy đặt bàn"
            }
        }

class PolicyTypeUpdate(BaseModel):
    type_name: str | None = None
    description: str | None = None
    
    @field_validator("type_name")
    def validate_type_name(cls, value):
        if value is None:
            return value
        allowed_types = {
            "Cancellation", "Deposit", "Dress Code", "Late Arrival", "No Show",
            "Reservation Time Limit", "Minimum Spend", "Group Size"
        }
        if value not in allowed_types:
            raise ValueError(f"type_name must be one of {allowed_types}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "type_name": "Deposit",
                "description": "Yêu cầu đặt cọc trước khi đặt bàn"
            }
        }

class PolicyTypeResponse(BaseModel):
    policy_type_id: int
    type_name: str

class PolicyTypeGetResponse(BaseModel):
    policy_type_id: int
    type_name: str
    description: str | None
    created_at: datetime

# PolicyType endpoints
@policy_type_router.post("/create_policy_type/", 
                         response_model=PolicyTypeResponse, 
                         summary="Create a new policy type")
async def create_policy_type(
    policy_type: PolicyTypeCreate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Create a new policy type."""
        db_policy_type = public_crud.create_policy_type(
            type_name=policy_type.type_name,
            description=policy_type.description
        )
        return {
            "policy_type_id": db_policy_type.policy_type_id,
            "type_name": db_policy_type.type_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_type_router.get("/get_policy_type/{policy_type_id}", 
                        response_model=PolicyTypeGetResponse, 
                        summary="Get a policy type by ID")
async def get_policy_type(
    policy_type_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific policy type by its ID."""
    policy_type = public_crud.get_policy_type(policy_type_id)
    if not policy_type:
        raise HTTPException(status_code=404, detail="Policy type not found")
    return {
        "policy_type_id": policy_type.policy_type_id,
        "type_name": policy_type.type_name,
        "description": policy_type.description,
        "created_at": policy_type.created_at
    }

@policy_type_router.put("/update_policy_type/{policy_type_id}", 
                        response_model=PolicyTypeResponse, 
                        summary="Update a policy type")
async def update_policy_type(
    policy_type_id: int,
    policy_type: PolicyTypeUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Update an existing policy type."""
        data = {k: v for k, v in policy_type.model_dump().items() if v is not None}
        db_policy_type = public_crud.update_policy_type(policy_type_id, data)
        if not db_policy_type:
            raise HTTPException(status_code=404, detail="Policy type not found")
        return {
            "policy_type_id": db_policy_type.policy_type_id,
            "type_name": db_policy_type.type_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@policy_type_router.delete("/delete_policy_type/{policy_type_id}", summary="Delete a policy type")
async def delete_policy_type(
    policy_type_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Delete a policy type."""
        deleted = public_crud.delete_policy_type(policy_type_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Policy type not found")
        return {"message": f"Policy type deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")