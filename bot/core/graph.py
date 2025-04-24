# BOOKINGTABLE/bot/langgraph/graph.py
from langgraph.graph import StateGraph, END, START
from bot.core.state import BookingState
from langgraph.checkpoint.memory import MemorySaver

from bot.core.greeting_nodes import (
    welcome_node,
    introduce_node,
    support_node,
    get_user_intent_node
)

from bot.core.booking_nodes import (
    booking_node,
    get_user_booking_information_node,
    check_availble_table_node,
    booking_confirmation_node,
    suggest_alternative_node,
    get_user_confirmation_booking_node,
    add_customer_node,
    welcome_new_customer_node,
    welcome_old_customer_node,
    add_reservation_node,
    notify_reservation_successful_node,
    apologize_customer_node,
    get_customer_answer_for_suggestion_node,
    meet_again_node
)

from bot.core.modify_nodes import (
    modify_node,
    get_customer_phone_number_node,
    notify_wait_for_check_node,
    check_customer_node,
    notify_found_customer_node,
    notify_not_found_customer_node,
    check_booking_node,
    return_customer_reservation_modify_node,
    notify_not_found_booking_node,
    get_modfify_booking_info_node,
    update_reservation_node,
    notify_update_reservation_successful_node,
    apologize_update_reservation_node
)

from bot.core.cancel_nodes import (
    cancel_node,
    return_customer_reservation_cancel_node,
    get_cancel_reservation,
    warning_cancel,
    get_confirm_cancel_node,
    update_cancel_node,
    thank_you_for_not_cancel,
    notify_cancel_successful_node,
    notify_cancel_unsuccessful_node
)

from bot.core.router_nodes import (
    booking_intent_router,
    check_availble_table_router,
    confirm_booking_router,
    new_customer_router,
    check_reservation_successful_router,
    check_customer_answer_for_suggestion_router,
    exist_customer_router,
    exist_booking_router,
    update_successful_router,
    get_confirm_cancel_router,
    cancel_successful_router
)



def build_graph() -> StateGraph:

    builder = StateGraph(BookingState)
    # Greeting nodes
    builder.add_node("welcome_node", welcome_node)
    builder.add_node("introduce_node", introduce_node)
    builder.add_node("support_node", support_node)
    builder.add_node("get_user_intent_node", get_user_intent_node)
    builder.add_node("booking_intent_router", booking_intent_router)
    
    # Booking nodes
    builder.add_node("booking_node", booking_node)
    builder.add_node("get_booking_information_node", get_user_booking_information_node)
    builder.add_node("booking_confirmation_node", booking_confirmation_node)
    builder.add_node("get_user_confirmation_booking_node", get_user_confirmation_booking_node)
    builder.add_node("add_customer_node", add_customer_node)
    builder.add_node("welcome_new_customer_node", welcome_new_customer_node)
    builder.add_node("welcome_old_customer_node", welcome_old_customer_node)
    builder.add_node("add_reservation_node", add_reservation_node)
    builder.add_node("notify_reservation_successful_node", notify_reservation_successful_node)
    builder.add_node("apologize_customer_node", apologize_customer_node)
    builder.add_node("suggest_alternative_node", suggest_alternative_node)
    builder.add_node("get_customer_answer_for_suggestion_node", get_customer_answer_for_suggestion_node)
    builder.add_node("meet_again_node", meet_again_node)
    
    # Modify nodes
    builder.add_node("modify_node", modify_node)
    builder.add_node("get_customer_phone_number_node", get_customer_phone_number_node)
    builder.add_node("notify_wait_for_check_node", notify_wait_for_check_node)
    builder.add_node("check_customer_node", check_customer_node)
    builder.add_node("notify_found_customer_node", notify_found_customer_node)
    builder.add_node("notify_not_found_customer_node", notify_not_found_customer_node)
    builder.add_node("check_booking_node", check_booking_node)
    builder.add_node("return_customer_reservation_modify_node", return_customer_reservation_modify_node)
    builder.add_node("notify_not_found_booking_node", notify_not_found_booking_node)
    builder.add_node("get_modfify_booking_info_node", get_modfify_booking_info_node)
    builder.add_node("update_reservation_node", update_reservation_node)
    builder.add_node("notify_update_reservation_successful_node", notify_update_reservation_successful_node)
    builder.add_node("apologize_update_reservation_node", apologize_update_reservation_node)
    
    # Cancel nodes
    builder.add_node("cancel_node", cancel_node)
    builder.add_node("return_customer_reservation_cancel_node", return_customer_reservation_cancel_node)
    builder.add_node("get_cancel_reservation", get_cancel_reservation)
    builder.add_node("warning_cancel", warning_cancel)
    builder.add_node("get_confirm_cancel_node", get_confirm_cancel_node)
    builder.add_node("update_cancel_node", update_cancel_node)
    builder.add_node("thank_you_for_not_cancel", thank_you_for_not_cancel)
    builder.add_node("notify_cancel_successful_node", notify_cancel_successful_node)
    builder.add_node("notify_cancel_unsuccessful_node", notify_cancel_unsuccessful_node)
    
    # Router nodes
    builder.add_node("check_availble_table_node", check_availble_table_node)
    builder.add_node("check_availble_table_router", check_availble_table_router)
    builder.add_node("confirm_booking_router", confirm_booking_router)
    builder.add_node("new_customer_router", new_customer_router)
    builder.add_node("check_reservation_successful_router", check_reservation_successful_router)
    builder.add_node("check_customer_answer_for_suggestion_router", check_customer_answer_for_suggestion_router)
    
    builder.add_node("exist_customer_router", exist_customer_router)
    builder.add_node("exist_booking_router", exist_booking_router)
    builder.add_node("update_successful_router", update_successful_router)
    
    builder.add_node("get_confirm_cancel_router", get_confirm_cancel_router)
    builder.add_node("cancel_successful_router", cancel_successful_router)
    
    

    # Greeting flow
    builder.add_edge(START, "welcome_node")
    builder.add_edge("welcome_node", "introduce_node")
    builder.add_edge("introduce_node", "support_node")
    builder.add_edge("support_node", "get_user_intent_node")
    builder.add_edge("get_user_intent_node", "booking_intent_router")
    builder.add_conditional_edges(
        "booking_intent_router",
        lambda state: state.get("next_node", END), 
        {
            "booking": "booking_node",
            "modify": "modify_node",
            "cancel": "cancel_node",
            END: END
        }
    )
    
    # Booking flow
    builder.add_edge("booking_node", "get_booking_information_node")
    builder.add_edge("get_booking_information_node", "check_availble_table_node")
    builder.add_edge("check_availble_table_node", "check_availble_table_router")
    builder.add_conditional_edges(
        "check_availble_table_router",
        lambda state: state.get("next_node", END), 
        {
            "booking_confirmation_node": "booking_confirmation_node",
            "suggest_alternative_node": "suggest_alternative_node",
            END: END
        }
    )
    builder.add_edge("suggest_alternative_node", "get_customer_answer_for_suggestion_node")
    builder.add_edge("get_customer_answer_for_suggestion_node", "check_customer_answer_for_suggestion_router")
    builder.add_conditional_edges(
        "check_customer_answer_for_suggestion_router",
        lambda state: state.get("next_node", END), 
        {
            "booking_node": "booking_node",
            "meet_again_node": "meet_again_node",
            END: END
        }
    )
    builder.add_edge("meet_again_node", END)
    builder.add_edge("booking_confirmation_node", "get_user_confirmation_booking_node")
    builder.add_edge("get_user_confirmation_booking_node", "confirm_booking_router")
    builder.add_conditional_edges(
        "confirm_booking_router",
        lambda state: state.get("next_node", END), 
        {
            "add_customer_node": "add_customer_node",
            "booking_node": "booking_node",
            END: END
        }
    )
    builder.add_edge("add_customer_node", "new_customer_router")
    builder.add_conditional_edges(
        "new_customer_router",
        lambda state: state.get("next_node", END), 
        {
            "welcome_new_customer_node": "welcome_new_customer_node",
            "welcome_old_customer_node": "welcome_old_customer_node",
            END: END
        }
    )
    builder.add_edge("suggest_alternative_node", END)
    builder.add_edge("welcome_new_customer_node", "add_reservation_node")
    builder.add_edge("welcome_old_customer_node", "add_reservation_node")
    builder.add_edge("add_reservation_node", "check_reservation_successful_router")
    builder.add_conditional_edges(
        "check_reservation_successful_router",
        lambda state: state.get("next_node", END), 
        {
            "notify_reservation_successful_node": "notify_reservation_successful_node",
            "apologize_customer_node": "apologize_customer_node",
            END: END
        }
    )
    builder.add_edge("notify_reservation_successful_node", END)
    builder.add_edge("apologize_customer_node", END)
    
    # Modify flow
    builder.add_edge("modify_node", "get_customer_phone_number_node")
    builder.add_edge("get_customer_phone_number_node", "notify_wait_for_check_node")
    builder.add_edge("notify_wait_for_check_node", "check_customer_node")
    builder.add_edge("check_customer_node", "exist_customer_router")
    builder.add_conditional_edges(
        "exist_customer_router",
        lambda state: state.get("next_node", END), 
        {
            "notify_found_customer_node": "notify_found_customer_node",
            "notify_not_found_customer_node": "notify_not_found_customer_node",
            END: END
        }
    )
    builder.add_edge("notify_not_found_customer_node", "get_customer_phone_number_node")
    builder.add_edge("notify_found_customer_node", "check_booking_node")
    builder.add_edge("check_booking_node", "exist_booking_router")
    builder.add_conditional_edges(
        "exist_booking_router",
        lambda state: state.get("next_node", END), 
        {
            "return_customer_reservation_modify_node": "return_customer_reservation_modify_node",
            "return_customer_reservation_cancel_node": "return_customer_reservation_cancel_node",
            "notify_not_found_booking_node": "notify_not_found_booking_node",
            END: END
        }
    )
    builder.add_edge("notify_not_found_booking_node", "get_customer_phone_number_node")
    builder.add_edge("return_customer_reservation_modify_node", "get_modfify_booking_info_node")
    builder.add_edge("get_modfify_booking_info_node", "update_reservation_node")
    builder.add_edge("update_reservation_node", "update_successful_router")
    builder.add_conditional_edges(
        "update_successful_router",
        lambda state: state.get("next_node", END), 
        {
            "notify_update_reservation_successful_node": "notify_update_reservation_successful_node",
            "apologize_update_reservation_node": "apologize_update_reservation_node",
            END: END
        }
    )
    builder.add_edge("apologize_update_reservation_node", "get_modfify_booking_info_node")
    builder.add_edge("notify_update_reservation_successful_node", END)
    
    
    # Cancel flow
    builder.add_edge("cancel_node", "get_customer_phone_number_node")
    # get_customer_phone_number_node -> nodes in modify flow -> exist_booking_router
    builder.add_edge("return_customer_reservation_cancel_node", "get_cancel_reservation")
    builder.add_edge("get_cancel_reservation", "warning_cancel")
    builder.add_edge("warning_cancel", "get_confirm_cancel_node")
    builder.add_edge("get_confirm_cancel_node", "get_confirm_cancel_router")
    builder.add_conditional_edges(
        "get_confirm_cancel_router",
        lambda state: state.get("next_node", END), 
        {
            "update_cancel_node": "update_cancel_node",
            "thank_you_for_not_cancel": "thank_you_for_not_cancel",
            END: END
        }
    )
    builder.add_edge("thank_you_for_not_cancel", END)
    builder.add_edge("update_cancel_node", "cancel_successful_router")
    builder.add_conditional_edges(
        "cancel_successful_router",
        lambda state: state.get("next_node", END), 
        {
            "notify_cancel_successful_node": "notify_cancel_successful_node",
            "notify_cancel_unsuccessful_node": "notify_cancel_unsuccessful_node",
            END: END
        }
    )
    builder.add_edge("notify_cancel_unsuccessful_node", END)
    builder.add_edge("notify_cancel_successful_node", END)

    # Set up memory
    memory = MemorySaver()

    # Add
    graph = builder.compile(checkpointer=memory)
    
    return graph