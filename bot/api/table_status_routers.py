# BOOKINGTABLE/bot/api/table_status_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from pydantic import BaseModel, field_validator
from datetime import datetime

table_status_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

# Pydantic models cho TableStatus
class TableStatusCreate(BaseModel):
    table_id: int
    status: str
    
    @field_validator("status")
    def validate_status(cls, value):
        allowed_statuses = {"available", "reserved", "occupied", "needs_cleaning"}
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "table_id": 1,
                "status": "available"
            }
        }

class TableStatusUpdate(BaseModel):
    table_id: int | None = None
    status: str | None = None
    
    @field_validator("status")
    def validate_status(cls, value):
        if value is None:
            return value
        allowed_statuses = {"available", "reserved", "occupied", "needs_cleaning"}
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "status": "reserved"
            }
        }

class TableStatusResponse(BaseModel):
    status_id: int
    table_id: int
    status: str

class TableStatusGetResponse(BaseModel):
    status_id: int
    table_id: int
    status: str
    updated_at: datetime

# TableStatus endpoints
@table_status_router.post("/create_table_status/", 
                          response_model=TableStatusResponse, 
                          summary="Create a new table status")
async def create_table_status(
    table_status: TableStatusCreate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Create a new table status."""
        db_table_status = public_crud.create_table_status(
            table_id=table_status.table_id,
            status=table_status.status
        )
        return {
            "status_id": db_table_status.status_id,
            "table_id": db_table_status.table_id,
            "status": db_table_status.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@table_status_router.get("/get_table_status/{status_id}", 
                         response_model=TableStatusGetResponse, 
                         summary="Get a table status by ID")
async def get_table_status(
    status_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific table status by its ID."""
    table_status = public_crud.get_table_status(status_id)
    if not table_status:
        raise HTTPException(status_code=404, detail="Table status not found")
    return {
        "status_id": table_status.status_id,
        "table_id": table_status.table_id,
        "status": table_status.status,
        "updated_at": table_status.updated_at
    }

@table_status_router.put("/update_table_status/{status_id}", 
                         response_model=TableStatusResponse, 
                         summary="Update a table status")
async def update_table_status(
    status_id: int,
    table_status: TableStatusUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Update an existing table status."""
        data = {k: v for k, v in table_status.model_dump().items() if v is not None}
        db_table_status = public_crud.update_table_status(status_id, data)
        if not db_table_status:
            raise HTTPException(status_code=404, detail="Table status not found")
        return {
            "status_id": db_table_status.status_id,
            "table_id": db_table_status.table_id,
            "status": db_table_status.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@table_status_router.delete("/delete_table_status/{status_id}", summary="Delete a table status")
async def delete_table_status(
    status_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Delete a table status."""
        deleted = public_crud.delete_table_status(status_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Table status not found")
        return {"message": f"Table status deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")