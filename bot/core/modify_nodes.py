from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from bot.core.state import BookingState
from langgraph.types import interrupt
from datetime import datetime
import json
from bot.core.graph_function import (
    extract_phone_number,
    check_exist_customer_by_phone_number,
    get_reservations_of_customer,
    update_reservation_info,
    extract_modify_input_user
)

def modify_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    
    text = (
        "Quý khách vui lòng hãy cung cấp số điện thoại mà quý khách đã "
        f"sử dụng để đặt bàn tại nhà hàng {restaurant_name}.\n"
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def get_customer_phone_number_node(state: BookingState) -> BookingState:
    user_input = interrupt(None)
    
    phone_number = extract_phone_number(user_input)
    if phone_number is None:
        raise ValueError("Số điện thoại không đúng!!")
    
    state["booking_info"]["phone_number"] = phone_number
    state["user_input"] = user_input
    state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
    
    return state

def notify_wait_for_check_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    text = (
        f"Quý khách vui lòng chờ trong giây lát để nhà hàng {restaurant_name} "
        f"kiểm tra số điện thoại trong hệ thống đặt bàn."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state


def check_customer_node(state: BookingState) -> BookingState:
    customer = check_exist_customer_by_phone_number(state)
    
    if customer is not None:
        state["booking_info"]["customer_id"] = customer.customer_id
        state["booking_info"]["full_name"] = customer.name
        state["booking_info"]["email"] = customer.email or ""
    else:
        state["booking_info"]["customer_id"] = None
        state["booking_info"]["full_name"] = None
        state["booking_info"]["email"] = None
    
    return state

def notify_found_customer_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "")
    
    text = (
        f"Xin cảm ơn quý khách {customer_name} đã chờ đợi, ngay sau đây nhà hàng {restaurant_name} "
        f"sẽ kiểm tra thông tin đặt bàn của quý khách."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def notify_not_found_customer_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    text = (
        f"Xin cảm ơn quý khách đã chờ đợi, tuy nhiên nhà hàng {restaurant_name} "
        "không tìm ra thông tin của quý khách trong hệ thống của nhà hàng.\n"
        "Chúng tôi xin lỗi vì sự bất tiện này, quý khách vui lòng cung cấp lại số điện thoại "
        f"để nhà hàng {restaurant_name} kiểm tra lại số điện thoại của quý khách."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def check_booking_node(state: BookingState) -> BookingState:
    reservations = get_reservations_of_customer(state)
    
    if reservations is not None:
        state["list_reservations"] = reservations
        state["exist_reservation"] = True
    else:
        state["list_reservations"] = None
        state["exist_reservation"] = False
    
    return state

def return_customer_reservation_modify_node(state: BookingState) -> BookingState:
    list_reservations = state.get("list_reservations", None)
    # list_reservations = json.dumps(list_reservations)
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

def notify_not_found_booking_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    
    text = (
        f"Nhà hàng {restaurant_name} xin lỗi quý khách vì không thể tìm được thông tin đặt bàn của quý khách.\n"
        "Mong quý khách vui lòng nhập lại đúng số điện thoại mà quý khách dùng để đặt bàn để hệ thống của nhà hàng "
        "chúng tôi có thể tìm được thông tin đặt bàn của quý khách."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def get_modfify_booking_info_node(state: BookingState) -> BookingState:
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
            "party_size": int(update_info["party_size"]),
        }
        
    except (json.JSONDecodeError, ValueError):
        raise ValueError("Lỗi khi trích xuất thông tin khách hàng")

    user_request = json.dumps(update_info, ensure_ascii=False)
    state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_request)])
    state["user_input"] = user_request

    return state

def update_reservation_node(state: BookingState) -> BookingState:
    updated_reservation = update_reservation_info(state)
    state["modify_successful"] = False
    
    if updated_reservation is not None:
        state["modify_successful"] = True
    
    return state

def notify_update_reservation_successful_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "")
    reservation_date = state["booking_info"].get("reservation_date", "ngày đã đặt")
    reservation_time = state["booking_info"].get("reservation_time", "thời gian đã đặt")
    
    
    text = (
        f"Xin thông báo quý khách {customer_name} đã cập nhật đặt bàn thành công.\n"
        f"Nhà hàng {restaurant_name} rất mong chờ được phục vụ quý khách vào lúc "
        f"{reservation_time}, ngày {reservation_date}."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])

    return state

def apologize_update_reservation_node(state: BookingState) -> BookingState:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "")
    
    text = (
        f"Nhà hàng {restaurant_name} chân thành xin lỗi quý khách {customer_name} vì không thể tìm được "
        "thông tin đặt bàn của quý khách.\n"
        "Xin quý khách vui lòng chỉnh lại thông tin cập nhật đặt bàn một lần nữa.\n"
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])

    return state