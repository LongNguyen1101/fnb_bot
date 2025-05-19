# BOOKINGTABLE/bot/langgraph/state.py
from typing import TypedDict, Optional, Dict, Any, List, Annotated
from bot.schema.models import Reservation
from langgraph.graph.message import add_messages
import datetime

class BookingState(TypedDict):
    user_input: str
    messages: Annotated[list, add_messages]
    next_node: str
    intent: str
    state: str
    
    customer_psid: str
    customer_name: str
    customer_id: int
    salutation: str
    customer_phone_number: str
    
    date: str
    time: str
    people: str
    note: str
    inappropriate_information: List[str]
    missing_information: List[str]
    table_id: int
    table_number: str
    booking_successful: bool
    
    list_reservation: List[Dict[str, Any]]
    reservation_id_chosen: int
    modify_question: str
    modify_successful: bool
    
    cancel_successful: bool
    
def init_state() -> BookingState:
    return BookingState(
        user_input = "",
        messages = [],
        next_node = "",
        intent="",
        state=None,
        
        customer_psid=None,
        customer_name=None,
        customer_id=None,
        salutation=None,
        customer_phone_number=None,
        
        date=None,
        time=None,
        people=None,
        note=None,
        inappropriate_information=[],
        missing_information=[],
        table_id=None,
        table_number=None,
        booking_successful=None,
        
        list_reservation=[],
        reservation_id_chosen=None,
        modify_question=None,
        modify_successful=None,
        
        cancel_successful=None
    )