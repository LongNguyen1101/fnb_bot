# BOOKINGTABLE/bot/langgraph/state.py
from typing import TypedDict, Optional, Dict, Any, List
from datetime import date, time

class BookingState(TypedDict):
    user_input: str
    greeting_done: bool
    intro_done: bool
    
    table_id: Optional[int]
    customer_id: Optional[int]
    restaurant_id: int
    
    restaurant_info: Dict[str, Any]
    restaurant_branches: List[Dict[str, Any]]
    
    reservation_date: Optional[date]
    reservation_time: Optional[time]
    party_size: Optional[int]
    customer_name: Optional[str]
    customer_phone: Optional[str]
    customer_email: Optional[str]
    booking_confirmed: bool
    messages: list[Dict[str, Any]]  # Chat history