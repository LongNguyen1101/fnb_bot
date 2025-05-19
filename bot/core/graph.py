# BOOKINGTABLE/bot/langgraph/graph.py
from langgraph.graph import StateGraph, END, START
from bot.core.state import BookingState
from langgraph.checkpoint.memory import MemorySaver
from bot.core.booking_nodes import BookingDialogue
from bot.core.router_nodes import GraphRouter
from bot.core.start_nodes import StartDialogue
from bot.core.modify_nodes import ModifyDialogue
from bot.core.cancel_nodes import CancelDialogue

def build_graph() -> StateGraph:
    builder = StateGraph(BookingState)
    start = StartDialogue()
    booking = BookingDialogue()
    modify = ModifyDialogue()
    cancel = CancelDialogue()
    router = GraphRouter()
    
    # Start nodes
    builder.add_node("check_exists_customer_node", start.check_exists_customer_node)
    builder.add_node("announce_waiting_node", start.announce_waiting_node)
    builder.add_node("ask_for_salutation_node", start.ask_for_salutation_node)
    builder.add_node("get_salutation_node", start.get_salutation_node)
    builder.add_node("get_user_input_end_node", start.get_user_input_end_node)
    
    
    # Booking nodes
    builder.add_node("prepare_booking_node", booking.prepare_booking_node)
    builder.add_node("ask_phone_number_node", booking.ask_phone_number_node)
    builder.add_node("get_user_phone_number_node", booking.get_user_phone_number_node)
    builder.add_node("ask_phone_again_node", booking.ask_phone_again_node)
    builder.add_node("number_requireded_node", booking.number_requireded_node)
    builder.add_node("add_phone_number_node", booking.add_phone_number_node)
    builder.add_node("ask_booking_info_node", booking.ask_booking_info_node)
    builder.add_node("get_booking_info_node", booking.get_booking_info_node)
    builder.add_node("ask_for_correct_information_node", booking.ask_for_correct_information_node)
    builder.add_node("get_available_table_node", booking.get_available_table_node)
    builder.add_node("announce_no_available_table_node", booking.announce_no_available_table_node)
    builder.add_node("confirm_continue_booking_node", booking.confirm_continue_booking_node)
    builder.add_node("ask_again_booking_info_node", booking.ask_again_booking_info_node)
    builder.add_node("get_booking_again_info_node", booking.get_booking_again_info_node)
    builder.add_node("end_booking_with_thanks", booking.end_booking_with_thanks)
    builder.add_node("extract_booking_info_node", booking.extract_booking_info_node)
    builder.add_node("confirm_booking_node", booking.confirm_booking_node)
    builder.add_node("get_confirm_node", booking.get_confirm_node)
    builder.add_node("ask_edit_booking_info_node", booking.ask_edit_booking_info_node)
    builder.add_node("goodbye_node", booking.goodbye_node)
    builder.add_node("add_reservation_node", booking.add_reservation_node)
    builder.add_node("thank_you_booking_node", booking.thank_you_booking_node)
    builder.add_node("not_booking_successful_node", booking.not_booking_successful_node)
    
    # Modify nodes
    builder.add_node("announce_wait_to_get_reservation_node", modify.announce_wait_to_get_reservation_node)
    builder.add_node("get_reservation_node", modify.get_reservation_node)
    builder.add_node("notify_not_found_reservation_node", modify.notify_not_found_reservation_node)
    builder.add_node("ask_modify_reservation_node", modify.ask_modify_reservation_node)
    builder.add_node("get_modify_info_node", modify.get_modify_info_node)
    builder.add_node("ask_for_correct_modify_node", modify.ask_for_correct_modify_node)
    builder.add_node("get_available_table_modify_node", booking.get_available_table_node)
    builder.add_node("announce_no_available_table_modify_node", booking.announce_no_available_table_node)
    builder.add_node("get_confirm_continue_modify_node", booking.confirm_continue_booking_node)
    builder.add_node("end_modify_with_thanks", modify.end_modify_with_thanks)
    builder.add_node("ask_modify_again_info_node", modify.ask_modify_again_info_node)
    builder.add_node("get_modify_again_info_node", modify.get_modify_again_info_node)
    builder.add_node("extract_modify_info_node", modify.extract_modify_info_node)
    builder.add_node("confirm_modify_node", modify.confirm_modify_node)
    builder.add_node("get_confirm_modify_node", modify.get_confirm_modify_node)
    builder.add_node("ask_edit_modify_node", modify.ask_edit_modify_node)
    builder.add_node("end_modify_node", modify.end_modify_node)
    builder.add_node("update_reservation_node", modify.update_reservation_node)
    builder.add_node("thank_you_modify_node", modify.thank_you_modify_node)
    builder.add_node("not_modify_successful_node", modify.not_modify_successful_node)
    
    # Cancel nodes
    builder.add_node("announce_wait_to_get_reservation_cancel_node", modify.announce_wait_to_get_reservation_node)
    builder.add_node("get_reservation_cancel_node", modify.get_reservation_node)
    builder.add_node("notify_not_found_reservation_cancel_node", modify.notify_not_found_reservation_node)
    builder.add_node("ask_cancel_reservation_node", cancel.ask_cancel_reservation_node)
    builder.add_node("get_cancel_info_node", cancel.get_cancel_info_node)
    builder.add_node("ask_for_correct_cancel_node", modify.ask_for_correct_modify_node)
    builder.add_node("confirm_cancel_node", cancel.confirm_cancel_node)
    builder.add_node("get_confirm_cancel_node", cancel.get_confirm_cancel_node)
    builder.add_node("ask_edit_cancel_node", cancel.ask_edit_cancel_node)
    builder.add_node("end_cancel_node", modify.end_modify_node)
    builder.add_node("cancel_reservation_node", cancel.cancel_reservation_node)
    builder.add_node("thank_you_cancel_node", cancel.thank_you_cancel_node)
    builder.add_node("not_cancel_successful_node", cancel.not_cancel_successful_node)
    
    # ---------------------------------------------------------------------------------------------------------------
    
    # First router
    builder.add_node("first_intent_router", router.first_intent_router)
    builder.add_node("check_salutation_router", router.check_salutation_router)
    
    # Booking router
    builder.add_node("check_exists_phone_number", router.check_exists_phone_number)
    builder.add_node("check_user_phone_router", router.check_user_phone_router)
    builder.add_node("check_user_booking_router", router.check_user_booking_router)
    builder.add_node("check_available_table_router", router.check_available_table_router)
    builder.add_node("check_continue_booking_router", router.check_continue_booking_router)
    builder.add_node("check_user_confirm_router", router.check_user_confirm_router)
    builder.add_node("booking_successful_router", router.booking_successful_router)
    
    # Modify router
    builder.add_node("check_quantity_reservation_router", router.check_quantity_reservation_router)
    builder.add_node("check_user_modify_router", router.check_user_modify_router)
    builder.add_node("check_party_size_router", router.check_party_size_router)
    builder.add_node("check_available_table_modify_router", router.check_available_table_router)
    builder.add_node("check_continue_modify_router", router.check_continue_booking_router)
    builder.add_node("check_user_confirm_modify_router", router.check_user_confirm_modify_router)
    builder.add_node("modify_successful_router", router.modify_successful_router)
    
    # Cancel router
    builder.add_node("check_quantity_reservation_cancel_router", router.check_quantity_reservation_router)
    builder.add_node("check_user_cancel_router", router.check_user_cancel_router)
    builder.add_node("check_user_confirm_cancel_router", router.check_user_confirm_cancel_router)
    builder.add_node("cancel_successful_router", router.cancel_successful_router)
    
    # ---------------------------------------------------------------------------------------------------------------
    
    # First flow
    builder.add_edge(START, "announce_waiting_node")
    builder.add_edge("announce_waiting_node", "check_exists_customer_node")
    builder.add_edge("check_exists_customer_node", "check_salutation_router")
    builder.add_conditional_edges(
        "check_salutation_router",
        lambda state: state.get("next_node", END),
        {
            "no": "ask_for_salutation_node",
            "yes": "first_intent_router"
        }
    )
    builder.add_edge("ask_for_salutation_node", "get_salutation_node")
    builder.add_edge("get_salutation_node", "first_intent_router")
    builder.add_conditional_edges(
        "first_intent_router",
        lambda state: state.get("next_node", END),
        {
            "booking": "prepare_booking_node",
            "modify": "announce_wait_to_get_reservation_node",
            "cancel": "announce_wait_to_get_reservation_cancel_node"
        }
    )
    
    # ---------------------------------------------------------------------------------------------------------------
    
    # Booking flow
    # builder.add_edge(START, "prepare_booking_node")
    builder.add_edge("prepare_booking_node", "check_exists_phone_number")
    builder.add_conditional_edges(
        "check_exists_phone_number",
        lambda state: state.get("next_node", END),
        {
            "yes": "ask_booking_info_node",
            "no": "ask_phone_number_node",
            END: END
        }
    )
    builder.add_edge("ask_phone_number_node", "get_user_phone_number_node")
    builder.add_edge("get_user_phone_number_node", "check_user_phone_router")
    builder.add_conditional_edges(
        "check_user_phone_router",
        lambda state: state.get("next_node", END),
        {
            "wrong_number": "ask_phone_again_node",
            "need_number": "number_requireded_node",
            "not_relevant": END,
            "normal": "add_phone_number_node"
        }
    )
    builder.add_edge("ask_phone_again_node", "get_user_phone_number_node")
    builder.add_edge("number_requireded_node", "get_user_phone_number_node")
    builder.add_edge("add_phone_number_node", "ask_booking_info_node")
    builder.add_edge("ask_booking_info_node", "get_booking_info_node")
    builder.add_edge("get_booking_info_node", "check_user_booking_router")
    builder.add_conditional_edges(
        "check_user_booking_router",
        lambda state: state.get("next_node", END),
        {
            "inappropriate_information": "ask_for_correct_information_node",
            "normal": "get_available_table_node",
            "not_relevant": END,
        }
    )
    builder.add_edge("ask_for_correct_information_node", "get_booking_info_node")
    builder.add_edge("get_available_table_node", "check_available_table_router")
    builder.add_conditional_edges(
        "check_available_table_router",
        lambda state: state.get("next_node", END),
        {
            "yes": "confirm_booking_node",
            "no": "announce_no_available_table_node",
        }
    )
    builder.add_edge("announce_no_available_table_node", "confirm_continue_booking_node")
    builder.add_edge("confirm_continue_booking_node", "check_continue_booking_router")
    builder.add_conditional_edges(
        "check_continue_booking_router",
        lambda state: state.get("next_node", END),
        {
            "continue_without_info": "ask_again_booking_info_node",
            "no_continue": "end_booking_with_thanks",
            "continue_with_info": "extract_booking_info_node"
        }
    )
    builder.add_edge("ask_again_booking_info_node", "get_booking_again_info_node")
    builder.add_edge("get_booking_again_info_node", "check_user_booking_router")
    builder.add_edge("end_booking_with_thanks", END)
    builder.add_edge("extract_booking_info_node", "check_user_booking_router")
    
    builder.add_edge("confirm_booking_node", "get_confirm_node")
    builder.add_edge("get_confirm_node", "check_user_confirm_router")
    builder.add_conditional_edges(
        "check_user_confirm_router",
        lambda state: state.get("next_node", END),
        {
            "confirm": "add_reservation_node",
            "need_edit": "ask_edit_booking_info_node",
            "exit": "goodbye_node",
            "not_relevant": END,
             END: END
        }
    )
    builder.add_edge("goodbye_node", "get_user_input_end_node")
    builder.add_edge("ask_edit_booking_info_node", "get_booking_again_info_node")
    builder.add_edge("add_reservation_node", "booking_successful_router")
    builder.add_conditional_edges(
        "booking_successful_router",
        lambda state: state.get("next_node", END),
        {
            "successful": "thank_you_booking_node",
            "unsuccessful": "not_booking_successful_node",
            END: END
        }
    )
    builder.add_edge("thank_you_booking_node", "get_user_input_end_node")
    builder.add_edge("not_booking_successful_node", "get_user_input_end_node")
    
    # ---------------------------------------------------------------------------------------------------------------
    
    # Modify flow
    builder.add_edge("announce_wait_to_get_reservation_node", "get_reservation_node")
    builder.add_edge("get_reservation_node", "check_quantity_reservation_router")
    builder.add_conditional_edges(
        "check_quantity_reservation_router",
        lambda state: state.get("next_node", END),
        {
            "no_reservation": "notify_not_found_reservation_node",
            "reservation": "ask_modify_reservation_node",
            END: END
        }
    )
    builder.add_edge("notify_not_found_reservation_node", END)
    builder.add_edge("ask_modify_reservation_node", "get_modify_info_node")
    builder.add_edge("get_modify_info_node", "check_user_modify_router")
    builder.add_conditional_edges(
        "check_user_modify_router",
        lambda state: state.get("next_node", END),
        {
            "normal": "check_party_size_router",
            "inappropriate_information": "ask_for_correct_modify_node",
            END: END
        }
    )
    builder.add_edge("ask_for_correct_modify_node", "get_modify_info_node")
    builder.add_conditional_edges(
        "check_party_size_router",
        lambda state: state.get("next_node", END),
        {
            "greater": "get_available_table_modify_node",
            "smaller": "confirm_modify_node",
            END: END
        }
    )
    builder.add_edge("get_available_table_modify_node", "check_available_table_modify_router")
    builder.add_conditional_edges(
        "check_available_table_modify_router",
        lambda state: state.get("next_node", END),
        {
            "yes": "confirm_modify_node",
            "no": "announce_no_available_table_modify_node",
            END: END
        }
    )
    builder.add_edge("announce_no_available_table_modify_node", "get_confirm_continue_modify_node")
    builder.add_edge("get_confirm_continue_modify_node", "check_continue_modify_router")
    builder.add_conditional_edges(
        "check_continue_modify_router",
        lambda state: state.get("next_node", END),
        {
            "continue_without_info": "ask_modify_again_info_node",
            "no_continue": "end_modify_with_thanks",
            "continue_with_info": "extract_modify_info_node",
            END: END
        }
    )
    builder.add_edge("end_modify_with_thanks", END)
    builder.add_edge("ask_modify_again_info_node", "get_modify_again_info_node")
    builder.add_edge("get_modify_again_info_node", "check_user_modify_router")
    builder.add_edge("extract_modify_info_node", "check_user_modify_router")
    
    builder.add_edge("confirm_modify_node", "get_confirm_modify_node")
    builder.add_edge("get_confirm_modify_node", "check_user_confirm_modify_router")
    builder.add_conditional_edges(
        "check_user_confirm_modify_router",
        lambda state: state.get("next_node", END),
        {
            "confirm": "update_reservation_node",
            "need_edit": "ask_edit_modify_node",
            "exit": "end_modify_node",
            "not_relevant": END,
             END: END
        }
    )
    builder.add_edge("ask_edit_modify_node", "get_modify_again_info_node")
    builder.add_edge("end_modify_node", "get_user_input_end_node")
    builder.add_edge("update_reservation_node", "modify_successful_router")
    builder.add_conditional_edges(
        "modify_successful_router",
        lambda state: state.get("next_node", END),
        {
            "successful": "thank_you_modify_node",
            "unsuccessful": "not_modify_successful_node",
            END: END
        }
    )
    builder.add_edge("thank_you_modify_node", "get_user_input_end_node")
    builder.add_edge("not_modify_successful_node", "get_user_input_end_node")
    
    # ---------------------------------------------------------------------------------------------------------------
    
    # Cancel flow
    builder.add_edge("announce_wait_to_get_reservation_cancel_node", "get_reservation_cancel_node")
    builder.add_edge("get_reservation_cancel_node", "check_quantity_reservation_cancel_router")
    builder.add_conditional_edges(
        "check_quantity_reservation_cancel_router",
        lambda state: state.get("next_node", END),
        {
            "no_reservation": "notify_not_found_reservation_cancel_node",
            "reservation": "ask_cancel_reservation_node",
            END: END
        }
    )
    builder.add_edge("notify_not_found_reservation_cancel_node", END)
    builder.add_edge("ask_cancel_reservation_node", "get_cancel_info_node")
    builder.add_edge("get_cancel_info_node", "check_user_cancel_router")
    builder.add_conditional_edges(
        "check_user_cancel_router",
        lambda state: state.get("next_node", END),
        {
            "normal": "confirm_cancel_node",
            "inappropriate_information": "ask_for_correct_cancel_node",
            END: END
        }
    )
    builder.add_edge("ask_for_correct_cancel_node", "get_cancel_info_node")
    builder.add_edge("confirm_cancel_node", "get_confirm_cancel_node")
    builder.add_edge("get_confirm_cancel_node", "check_user_confirm_cancel_router")
    builder.add_conditional_edges(
        "check_user_confirm_cancel_router",
        lambda state: state.get("next_node", END),
        {
            "confirm": "cancel_reservation_node",
            "need_edit": "ask_edit_cancel_node",
            "exit": "end_cancel_node",
            "not_relevant": END,
             END: END
        }
    )
    builder.add_edge("ask_edit_cancel_node", END)
    builder.add_edge("end_cancel_node", "get_user_input_end_node")
    builder.add_edge("cancel_reservation_node", "cancel_successful_router")
    builder.add_conditional_edges(
        "cancel_successful_router",
        lambda state: state.get("next_node", END),
        {
            "successful": "thank_you_cancel_node",
            "unsuccessful": "not_cancel_successful_node",
            END: END
        }
    )
    builder.add_edge("thank_you_cancel_node", "get_user_input_end_node")
    builder.add_edge("not_cancel_successful_node", "get_user_input_end_node")
    
    
    builder.add_edge("get_user_input_end_node", "first_intent_router")
    
    
    
    # Set up memory
    memory = MemorySaver()

    # Add
    graph = builder.compile(checkpointer=memory)
    
    return graph