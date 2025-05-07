# BOOKINGTABLE/bot/api/table_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from typing import Dict, Any
from pydantic import BaseModel

table_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

# Pydantic models cho Table
class TableCreate(BaseModel):
    branch_id: int
    table_number: str
    capacity: int
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "branch_id": 1,
                "table_number": "T01",
                "capacity": 4,
                "is_active": True
            }
        }

class TableUpdate(BaseModel):
    branch_id: int | None = None
    table_number: str | None = None
    capacity: int | None = None
    is_active: bool | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "table_number": "T02",
                "capacity": 6
            }
        }

class TableResponse(BaseModel):
    table_id: int
    branch_id: int
    table_number: str

class TableGetResponse(BaseModel):
    table_id: int
    branch_id: int
    table_number: str
    capacity: int
    is_active: bool

# Table endpoints
@table_router.post("/create_tables/", response_model=TableResponse, summary="Create a new table")
async def create_table(
    table: TableCreate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Create a new table."""
        db_table = public_crud.create_table(
            branch_id=table.branch_id,
            table_number=table.table_number,
            capacity=table.capacity,
            is_active=table.is_active
        )
        return {
            "table_id": db_table.table_id,
            "branch_id": db_table.branch_id,
            "table_number": db_table.table_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@table_router.get("/get_tables/{table_id}", response_model=TableGetResponse, summary="Get a table by ID")
async def get_table(
    table_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific table by its ID."""
    table = public_crud.get_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return {
        "table_id": table.table_id,
        "branch_id": table.branch_id,
        "table_number": table.table_number,
        "capacity": table.capacity,
        "is_active": table.is_active
    }

@table_router.put("/update_tables/{table_id}", response_model=TableResponse, summary="Update a table")
async def update_table(
    table_id: int,
    table: TableUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Update an existing table."""
        data = {k: v for k, v in table.model_dump().items() if v is not None}
        db_table = public_crud.update_table(table_id, data)
        if not db_table:
            raise HTTPException(status_code=404, detail="Table not found")
        return {
            "table_id": db_table.table_id,
            "branch_id": db_table.branch_id,
            "table_number": db_table.table_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@table_router.delete("/delete_tables/{table_id}", summary="Delete a table")
async def delete_table(
    table_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Delete a table."""
        deleted = public_crud.delete_table(table_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Table not found")
        return {"message": f"Table deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")