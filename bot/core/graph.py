# BOOKINGTABLE/bot/langgraph/graph.py
from langgraph.graph import StateGraph, END
from .state import BookingState
from .nodes import (
    greet_customer,
    introduce_restaurant,
    find_table,
    collect_customer_info,
    confirm_booking
)

def route_state(state: BookingState) -> str:
    if not state.get("greeting_done", False):
        return "greet"
    if not state.get("intro_done", False):
        return "introduce"
    if not state.get("table_id"):
        return "find_table"
    if not state.get("customer_id"):
        return "collect_info"
    if not state.get("booking_confirmed", False):
        return "confirm"
    return END

def build_graph() -> StateGraph:
    graph = StateGraph(BookingState)

    graph.add_node("greet", greet_customer)
    graph.add_node("introduce", introduce_restaurant)
    graph.add_node("find_table", find_table)
    graph.add_node("collect_info", collect_customer_info)
    graph.add_node("confirm", confirm_booking)

    graph.set_entry_point("greet")

    graph.add_conditional_edges("greet", route_state)
    graph.add_conditional_edges("introduce", route_state)
    graph.add_conditional_edges("find_table", route_state)
    graph.add_conditional_edges("collect_info", route_state)
    graph.add_conditional_edges("confirm", route_state)

    return graph.compile()