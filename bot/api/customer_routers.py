# BOOKINGTABLE/bot/api/customer_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from typing import Dict, Any
from pydantic import BaseModel, field_validator, EmailStr
from datetime import datetime

customer_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

# Pydantic models cho Customer
class CustomerCreate(BaseModel):
    name: str
    phone_number: str
    email: EmailStr | None = None
    
    @field_validator("name")
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value
    
    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if not value.strip():
            raise ValueError("Phone number cannot be empty")
        if not value.replace("+", "").replace(" ", "").isdigit():
            raise ValueError("Phone number must contain only digits and optional '+' prefix")
        if len(value.replace(" ", "")) < 7 or len(value.replace(" ", "")) > 15:
            raise ValueError("Phone number must be between 7 and 15 characters")
        return value
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Nguyen Van A",
                "phone_number": "+84912345678",
                "email": "nguyenvana@example.com"
            }
        }

class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    is_vip: bool | None = None
    
    @field_validator("name")
    def validate_name(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value
    
    @field_validator("phone_number")
    def validate_phone_number(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Phone number cannot be empty")
        if not value.replace("+", "").replace(" ", "").isdigit():
            raise ValueError("Phone number must contain only digits and optional '+' prefix")
        if len(value.replace(" ", "")) < 7 or len(value.replace(" ", "")) > 15:
            raise ValueError("Phone number must be between 7 and 15 characters")
        return value
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Nguyen Van B",
                "phone_number": "+84987654321",
                "is_vip": True
            }
        }

class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    phone_number: str

class CustomerGetResponse(BaseModel):
    customer_id: int
    name: str
    phone_number: str
    email: str | None
    is_vip: bool
    created_at: datetime

# Customer endpoints
@customer_router.post("/create_customer/", response_model=CustomerResponse, summary="Create a new customer")
async def create_customer(
    customer: CustomerCreate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Create a new customer."""
        db_customer = public_crud.create_customer(
            name=customer.name,
            phone_number=customer.phone_number,
            email=customer.email
        )
        return {
            "customer_id": db_customer.customer_id,
            "name": db_customer.name,
            "phone_number": db_customer.phone_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@customer_router.get("/get_customer/{customer_id}", response_model=CustomerGetResponse, summary="Get a customer by ID")
async def get_customer(
    customer_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific customer by its ID."""
    customer = public_crud.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "phone_number": customer.phone_number,
        "email": customer.email,
        "is_vip": customer.is_vip,
        "created_at": customer.created_at
    }

@customer_router.put("/update_customer/{customer_id}", response_model=CustomerResponse, summary="Update a customer")
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Update an existing customer."""
        data = {k: v for k, v in customer.model_dump().items() if v is not None}
        db_customer = public_crud.update_customer(customer_id, data)
        if not db_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return {
            "customer_id": db_customer.customer_id,
            "name": db_customer.name,
            "phone_number": db_customer.phone_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@customer_router.delete("/delete_customer/{customer_id}", summary="Delete a customer")
async def delete_customer(
    customer_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Delete a customer."""
        deleted = public_crud.delete_customer(customer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Customer not found")
        return {"message": f"Customer deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")