# BOOKINGTABLE/bot/api/restaurant_branches_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD  
from typing import Dict, Any
from pydantic import BaseModel

restaurant_branches_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

# Pydantic models cho RestaurantBranch
class RestaurantBranchCreate(BaseModel):
    restaurant_id: int
    address: str
    opening_time: str  # "HH:MM:SS"
    closing_time: str  # "HH:MM:SS"
    max_capacity: int
    
    class Config: 
        schema_extra = {
            "example": {
                "restaurant_id": 1,
                "address": "123 Đường Lê Lợi, Quận 1, TP.HCM",
                "opening_time": "10:00:00",
                "closing_time": "22:00:00",
                "max_capacity": 50
            }
        }

class RestaurantBranchUpdate(BaseModel):
    restaurant_id: int | None = None
    address: str | None = None
    opening_time: str | None = None
    closing_time: str | None = None
    max_capacity: int | None = None
    
    class Config:
        schema_extra = {
            "example": {
                "address": "456 Đường Nguyễn Huệ, Quận 1, TP.HCM",
                "max_capacity": 60
            }
        }

class RestaurantBranchResponse(BaseModel):
    branch_id: int
    restaurant_id: int
    address: str

class RestaurantBranchGetResponse(BaseModel):
    branch_id: int
    restaurant_id: int
    address: str
    opening_time: str
    closing_time: str
    max_capacity: int

# RestaurantBranch endpoints
@restaurant_branches_router.post("/create_restaurant_branches/", 
                                 response_model=RestaurantBranchResponse, 
                                 summary="Create a new restaurant branch")
async def create_restaurant_branch(
    branch: RestaurantBranchCreate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Create a new restaurant branch."""
        db_branch = public_crud.create_restaurant_branches(
            restaurant_id=branch.restaurant_id,
            address=branch.address,
            opening_time=branch.opening_time,
            closing_time=branch.closing_time,
            max_capacity=branch.max_capacity
        )
        return {
            "branch_id": db_branch.branch_id,
            "restaurant_id": db_branch.restaurant_id,
            "address": db_branch.address
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@restaurant_branches_router.get("/get_restaurant_branches/{branch_id}", 
                                response_model=RestaurantBranchGetResponse, 
                                summary="Get a restaurant branch by ID")
async def get_restaurant_branch(
    branch_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific restaurant branch by its ID."""
    branch = public_crud.get_restaurant_branches(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Restaurant branch not found")
    return {
        "branch_id": branch.branch_id,
        "restaurant_id": branch.restaurant_id,
        "address": branch.address,
        "opening_time": branch.opening_time.strftime("%H:%M:%S"),
        "closing_time": branch.closing_time.strftime("%H:%M:%S"),
        "max_capacity": branch.max_capacity
    }

@restaurant_branches_router.put("update_restaurant_branches/{branch_id}", 
                                response_model=RestaurantBranchResponse, 
                                summary="Update a restaurant branch")
async def update_restaurant_branch(
    branch_id: int,
    branch: RestaurantBranchUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Update an existing restaurant branch."""
        data = {k: v for k, v in branch.model_dump().items() if v is not None}
        db_branch = public_crud.update_restaurant_branches(branch_id, data)
        if not db_branch:
            raise HTTPException(status_code=404, detail="Restaurant branch not found")
        return {
            "branch_id": db_branch.branch_id,
            "restaurant_id": db_branch.restaurant_id,
            "address": db_branch.address
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@restaurant_branches_router.delete("/delete_restaurant_branches/{branch_id}", summary="Delete a restaurant branch")
async def delete_restaurant_branch(
    branch_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Delete a restaurant branch."""
        deleted = public_crud.delete_restaurant_branches(branch_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Restaurant branch not found")
        return {"message": f"Restaurant branch deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")