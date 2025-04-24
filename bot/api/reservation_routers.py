# BOOKINGTABLE/bot/api/reservation_routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from typing import Dict, Any, List
from pydantic import BaseModel, field_validator
from datetime import date, time, datetime

reservation_router = APIRouter()

# Dependency injection
def get_public_crud(db: Session = Depends(get_db)):
    return PublicCRUD(db)

# Pydantic models cho Reservation
class ReservationCreate(BaseModel):
    table_id: int
    customer_id: int
    branch_id: int
    policy_id: int
    reservation_date: date
    reservation_time: time
    party_size: int
    status: str = "pending"
    
    @field_validator("party_size")
    def validate_party_size(cls, value):
        if value <= 0:
            raise ValueError("party_size must be greater than 0")
        return value
    
    @field_validator("status")
    def validate_status(cls, value):
        allowed_statuses = {"pending", "confirmed", "cancelled", "no_show", "completed"}
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "table_id": 1,
                "customer_id": 1,
                "branch_id": 1,
                "policy_id": 1,
                "reservation_date": "2025-04-10",
                "reservation_time": "18:00:00",
                "party_size": 4,
                "status": "pending"
            }
        }

class ReservationUpdate(BaseModel):
    table_id: int | None = None
    customer_id: int | None = None
    branch_id: int | None = None
    policy_id: int | None = None
    reservation_date: date | None = None
    reservation_time: time | None = None
    party_size: int | None = None
    status: str | None = None
    confirmed_at: datetime | None = None
    reminder_sent: bool | None = None
    
    @field_validator("party_size")
    def validate_party_size(cls, value):
        if value is None:
            return value
        if value <= 0:
            raise ValueError("party_size must be greater than 0")
        return value
    
    @field_validator("status")
    def validate_status(cls, value):
        if value is None:
            return value
        allowed_statuses = {"pending", "confirmed", "cancelled", "no_show", "completed"}
        if value not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "status": "confirmed",
                "confirmed_at": "2025-04-10T12:00:00",
                "reminder_sent": True
            }
        }

class ReservationResponse(BaseModel):
    reservation_id: int
    table_id: int | None
    customer_id: int | None
    branch_id: int
    status: str

class ReservationGetResponse(BaseModel):
    reservation_id: int
    table_id: int | None
    customer_id: int | None
    branch_id: int
    policy_id: int | None
    reservation_date: date
    reservation_time: time
    party_size: int
    status: str
    created_at: datetime
    confirmed_at: datetime | None
    reminder_sent: bool

# Reservation endpoints
@reservation_router.post("/create_reservation/", 
                         response_model=ReservationResponse, 
                         summary="Create a new reservation")
async def create_reservation(
    reservation: ReservationCreate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Create a new reservation."""
        db_reservation = public_crud.create_reservation(
            table_id=reservation.table_id,
            customer_id=reservation.customer_id,
            branch_id=reservation.branch_id,
            policy_id=reservation.policy_id,
            reservation_date=reservation.reservation_date,
            reservation_time=reservation.reservation_time,
            party_size=reservation.party_size,
            status=reservation.status
        )
        return {
            "reservation_id": db_reservation.reservation_id,
            "table_id": db_reservation.table_id,
            "customer_id": db_reservation.customer_id,
            "branch_id": db_reservation.branch_id,
            "status": db_reservation.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@reservation_router.get("/get_reservation/{reservation_id}", 
                        response_model=ReservationGetResponse, 
                        summary="Get a reservation by ID")
async def get_reservation(
    reservation_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific reservation by its ID."""
    reservation = public_crud.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {
        "reservation_id": reservation.reservation_id,
        "table_id": reservation.table_id,
        "customer_id": reservation.customer_id,
        "branch_id": reservation.branch_id,
        "policy_id": reservation.policy_id,
        "reservation_date": reservation.reservation_date,
        "reservation_time": reservation.reservation_time,
        "party_size": reservation.party_size,
        "status": reservation.status,
        "created_at": reservation.created_at,
        "confirmed_at": reservation.confirmed_at,
        "reminder_sent": reservation.reminder_sent
    }
    
@reservation_router.get("/get_reservation_by_customer_id/{customer_id}", 
                        response_model=List[ReservationGetResponse],
                        summary="Get a reservation by ID")
async def get_reservation(
    customer_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    """Retrieve details of a specific reservation by its ID."""
    list_reservation = public_crud.get_reservation_by_customer_id(customer_id)
    if not list_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return [
        {
            "reservation_id": reservation.reservation_id,
            "table_id": reservation.table_id,
            "customer_id": reservation.customer_id,
            "branch_id": reservation.branch_id,
            "policy_id": reservation.policy_id,
            "reservation_date": reservation.reservation_date,
            "reservation_time": reservation.reservation_time,
            "party_size": reservation.party_size,
            "status": reservation.status,
            "created_at": reservation.created_at,
            "confirmed_at": reservation.confirmed_at,
            "reminder_sent": reservation.reminder_sent
        } for reservation in list_reservation
    ]

@reservation_router.put("/update_reservation/{reservation_id}", 
                        response_model=ReservationResponse,
                        summary="Update a reservation")
async def update_reservation(
    reservation_id: int,
    reservation: ReservationUpdate,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Update an existing reservation."""
        data = {k: v for k, v in reservation.model_dump().items() if v is not None}
        db_reservation = public_crud.update_reservation(reservation_id, data)
        if not db_reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return {
            "reservation_id": db_reservation.reservation_id,
            "table_id": db_reservation.table_id,
            "customer_id": db_reservation.customer_id,
            "branch_id": db_reservation.branch_id,
            "status": db_reservation.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@reservation_router.delete("/delete_reservation/{reservation_id}", summary="Delete a reservation")
async def delete_reservation(
    reservation_id: int,
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    try:
        """Delete a reservation."""
        deleted = public_crud.delete_reservation(reservation_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return {"message": f"Reservation {reservation_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")