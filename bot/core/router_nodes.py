from bot.core.state import BookingState
from langgraph.graph import END


# ROUTER
def booking_intent_router(state: BookingState) -> BookingState:
    customer_want = state.get("customer_want", "")
    print(f"> Khách muốn: {customer_want}")
    next_node = END
    
    if customer_want == "booking":
        next_node = "booking"
    elif customer_want == "modify":
        next_node = "modify"
    elif customer_want == "cancel":
        next_node = "cancel"
    
    state["next_node"] = next_node
    return state

def check_availble_table_router(state: BookingState) -> BookingState:
    table_available = state.get("table_available", "")
    print(f"> Bàn có sẵn không: {table_available}")
    next_node = END
    
    if table_available is True:
        next_node = "booking_confirmation_node"
    else:
        next_node = "suggest_alternative_node"
    
    state["next_node"] = next_node
    return state
    
def confirm_booking_router(state: BookingState) -> BookingState:
    intent = state.get("intent", "")
    print(f"> Khách có đồng ý hay không: {intent}")
    next_node = END
    
    if intent == "YES":
        next_node = "add_customer_node"
    elif intent == "NO":
        next_node = "booking_node"
    
    state["next_node"] = next_node
    return state

def new_customer_router(state: BookingState) -> BookingState:
    new_customer = state.get("new_customer", "")
    print(f"> Có phải là khách mới không: {new_customer}")
    next_node = END
    
    if new_customer is True:
        next_node = "welcome_new_customer_node"
    else:
        next_node = "welcome_old_customer_node"
    
    state["next_node"] = next_node
    return state

def check_reservation_successful_router(state: BookingState) -> BookingState:
    reservation_successful = state.get("reservation_successful", "")
    print(f"> Đật bàn thành công không: {reservation_successful}")
    next_node = END
    
    if reservation_successful is True:
        next_node = "notify_reservation_successful_node"
    else:
        next_node = "apologize_customer_node"
    
    state["next_node"] = next_node
    return state

def check_customer_answer_for_suggestion_router(state: BookingState) -> BookingState:
    intent = state.get("intent", "")
    print(f"> Khách có muốn đặt lại không: {intent}")
    next_node = END
    
    if intent == "yes":
        next_node = "booking_node"
    else:
        next_node = "meet_again_node"
    
    state["next_node"] = next_node
    return state

def exist_customer_router(state: BookingState) -> BookingState:
    customer_id = state["booking_info"].get("customer_id", None)
    exist_customer = True if customer_id else False
    
    print(f"> Khách có tồn tại không: {exist_customer}")
    next_node = END
    
    if exist_customer is True:
        next_node = "notify_found_customer_node"
    else:
        next_node = "notify_not_found_customer"
    
    state["next_node"] = next_node
    return state

def exist_booking_router(state: BookingState) -> BookingState:
    exist_reservation = state.get("exist_reservation", False)
    customer_want = state.get("customer_want", None)
    
    print(f"> Có tồn tại đặt bàn không: {exist_reservation}")
    next_node = END
    
    if customer_want == "modify":
        if exist_reservation is True:
            next_node = "return_customer_reservation_modify_node"
        else:
            next_node = "notify_not_found_booking_node"
    elif customer_want == "cancel":
        if exist_reservation is True:
            next_node = "return_customer_reservation_cancel_node"
        else:
            next_node = "notify_not_found_booking_node"
    
    state["next_node"] = next_node
    return state

def update_successful_router(state: BookingState) -> BookingState:
    modify_successful = state.get("modify_successful", False)
    print(f"> Cập nhật đặt bàn thành công không: {modify_successful}")
    next_node = END
    
    if modify_successful is True:
        next_node = "notify_update_reservation_successful_node"
    else:
        next_node = "apologize_update_reservation_node"
    
    state["next_node"] = next_node  
    return state

def get_confirm_cancel_router(state: BookingState) -> BookingState:
    intent = state.get("intent", "")
    print(f"> Khách có đồng ý huỷ bàn hay không: {intent}")
    next_node = END
    
    if intent == "YES":
        next_node = "update_cancel_node"
    elif intent == "NO":
        next_node = "thank_you_for_not_cancel"
    
    state["next_node"] = next_node
    return state

def cancel_successful_router(state: BookingState) -> BookingState:
    cancel_successful = state.get("cancel_successful", False)
    print(f"> Xoá đặt bàn thành công không: {cancel_successful}")
    next_node = END
    
    if cancel_successful is True:
        next_node = "notify_cancel_successful_node"
    else:
        next_node = "notify_cancel_unsuccessful_node"
    
    state["next_node"] = next_node  
    return state