# BOOKINGTABLE/bot/langgraph/state.py
from typing import TypedDict, Optional, Dict, Any, List, Annotated
from bot.schema.models import Reservation
from langgraph.graph.message import add_messages
import datetime

class BookingInfo(TypedDict):
    branch_id: int
    address: str
    customer_id: int
    reservation_date: datetime.datetime
    reservation_time: str
    party_size: int
    
    full_name: str
    phone_number: str
    email: str
    
    table_id: int
    table_number: str
    table_capacity: int
    reservation_id_chosen: int

class BookingState(TypedDict):
    user_input: str
    messages: Annotated[list, add_messages]
    next_node: str
    new_customer: bool
    customer_id: int
    customer_want: str
    
    restaurant_info: Dict[str, Any]
    restaurant_branches: List[Dict[str, Any]]
    
    # For booking nodes
    intent : str
    booking_info: Dict[str, Any]
    table_available: bool
    reservation_successful: bool
    
    # For modify nodes
    list_reservations: List[Reservation]
    exist_reservation: bool
    modify_successful: bool
    
    # For cancel nodes
    cancel_successful: bool
    
def default_booking_info() -> BookingInfo:
    return BookingInfo(
        branch_id = 0,
        address = "",
        customer_id = 0,
        reservation_date = None,
        reservation_time = "",
        party_size = 0,
        full_name = "",
        phone_number = "",
        email = "",
        table_id = 0,
        table_number = "",
        table_capacity = 0,
        reservation_id_chosen = 0
    )
    
def init_state() -> BookingState:
    return BookingState(
        user_input = "",
        messages = [],
        next_node = "",
        new_customer = None,
        customer_id = None,
        
        restaurant_info = None,
        restaurant_branches = None,
        
        intent = "",
        booking_info = default_booking_info(),
        table_available = None,
        reservation_successful = None,
        
        list_reservations = None,
        exist_reservation = None,
        modify_successful = None,
        
        cancel_successful = None
    )