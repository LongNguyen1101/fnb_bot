from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from bot.core.state import BookingState
from langgraph.types import interrupt
from datetime import datetime
import json
from bot.core.graph_function import (
    cancel_reservation,
    extract_modify_input_user
)


def cancel_node(state: BookingState):
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    
    text = (
        "Quý khách vui lòng hãy cung cấp số điện thoại mà quý khách đã "
        f"sử dụng để đặt bàn tại nhà hàng {restaurant_name}.\n"
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def return_customer_reservation_cancel_node(state: BookingState) -> BookingState:
    list_reservations = state.get("list_reservations", None)
    
    text = ""
    for reservation in list_reservations:
        try:
            text += (
                f"Thông tin đặt bàn số: {reservation['reservation_id']}\n"
                f"Chi nhánh: {reservation['branch_id']}\n"
                f"Địa chỉ: {reservation['address']}\n"
                f"Ngày đặt: {reservation['reservation_date']}\n"
                f"Thời gian đặt: {reservation['reservation_time']}\n"
                f"Số lượng người: {reservation['party_size']}\n\n"
            )
        except KeyError as e:
            text += f"Lỗi: Thiếu thông tin cho đặt bàn (thiếu key: {e})\n\n"

    if not list_reservations:
        text += "Không có thông tin đặt bàn nào.\n"

    text += "Quý khách hãy sửa đổi thông tin đặt bàn theo mong muốn của quý khách."
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def get_cancel_reservation(state: BookingState) -> BookingState:
    update_info = interrupt(None)
    update_info = extract_modify_input_user(update_info)
    update_info = json.loads(update_info)
    print("update info", update_info)
    
    try:
        # update_info = json.loads(user_request)
        # Kiểm tra các trường cần thiết
        if not all(key in update_info for key in ["branch_id", "address", "reservation_date",
                                                  "reservation_time", "party_size", "reservation_id_chosen"]):
            raise ValueError("JSON thiếu các trường cần thiết")
        
        parse_reservation_date = datetime.strptime(update_info["reservation_date"], "%d/%m/%Y")
        
        # Lưu thông tin đặt bàn vào state
        state["booking_info"] = {
            "reservation_id_chosen": int(update_info["reservation_id_chosen"]),
            "branch_id": int(update_info["branch_id"]),
            "address": update_info["address"],
            "reservation_date": parse_reservation_date,
            "reservation_time": update_info["reservation_time"],
            "party_size": int(update_info["party_size"])
        }
        
    except (json.JSONDecodeError, ValueError):
        raise ValueError("Lỗi khi trích xuất thông tin khách hàng")

    user_request = json.dumps(update_info, ensure_ascii=False)
    state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_request)])
    state["user_input"] = user_request

    return state

def warning_cancel(state: BookingState) -> BookingState:
    customer_name = state["booking_info"].get("full_name", "")
    
    parse_reservation_date = state["booking_info"]["reservation_date"].strftime('%d/%m/%Y')
    
    text = (
        f"Quý khách {customer_name} có chắc chắn muốn huỷ thông tin đặt bàn dưới đây không:\n"
        f"- Địa chỉ chi nhánh: {state["booking_info"]["address"]}\n"
        f"- Ngày đặt bàn: {parse_reservation_date}\n"
        f"- Thòi gian đặt bàn: {state["booking_info"]["reservation_time"]}\n"
        f"- Số lượng người: {state["booking_info"]["party_size"]}\n"
        "Xin quý khách cân nhắc thật kỹ trước khi quyết định huỷ đặt bàn."
    ).strip()
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def get_confirm_cancel_node(state: BookingState) -> BookingState:
    user_response = interrupt(None)
    
    if user_response != "YES" and user_response != "NO":
        raise ValueError("Invalid user response!")
    
    state["user_input"] = user_response
    state["intent"] = user_response
    return state

def update_cancel_node(state: BookingState) -> BookingState:
    cancelled_reservation = cancel_reservation(state)
    state["cancel_successful"] = False
    
    if cancelled_reservation is not None:
        state["cancel_successful"] = True
    
    return state

def thank_you_for_not_cancel(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "")
    parse_reservation_date = state["booking_info"]["reservation_date"].strftime('%d/%m/%Y')
    
    text = (
        f"Xin chân thành cảm ơn quý khách {customer_name} đã suy nghĩ lại và quyết định không huỷ bàn "
        f"tại nhà hàng {restaurant_name}.\n"
        f"Nhà hàng chúng tôi rất mong chờ được gặp quý khách vào {parse_reservation_date}"
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def notify_cancel_successful_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "")
    reservation_time = state["booking_info"].get("reservation_time", "thời gian đã đặt")
    parse_reservation_date = state["booking_info"]["reservation_date"].strftime('%d/%m/%Y')
    
    text = (
        f"Xin thông báo quý khách {customer_name} đã huỷ đặt bàn thành công.\n"
        f"Nhà hàng {restaurant_name} rất tiếc vì không thể phục vụ được quý khách vào lúc "
        f"{reservation_time}, ngày {parse_reservation_date}.\n"
        "Chúng tôi mong chờ được phục vụ quý khách một ngày không xa.\n"
        "Trong quá trình đặt bàn, nếu quý khách có bất kỳ điều gì không hài lòng "
        "thì hãy liên hệ với chúng tôi.\n"
        f"Nhà hàng {restaurant_name} xin cảm ơn vì đã được phục vụ quý khách {customer_name}."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def notify_cancel_unsuccessful_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "")
    
    text = (
        f"Nhà hàng {restaurant_name} chân thành xin lỗi quý khách {customer_name} vì không thể tìm được "
        "thông tin đặt bàn của quý khách.\n"
        "Xin quý khách vui lòng chọn lại thông tin đặt bàn mà quý khách muốn huỷ một lần nữa.\n"
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])

    return state