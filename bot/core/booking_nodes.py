from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from bot.core.state import BookingState
from langgraph.types import interrupt
import json
from datetime import datetime
from bot.core.graph_function import (
    find_available_table,
    check_exist_customer_by_phone_number,
    add_customer,
    add_reservation,
    get_notify_reservation_successful,
    classify_intent_for_suggestion,
    get_meet_again_text
)

# BOOKING NODES
def booking_node(state: BookingState):
    request = (
        "Quý khách hãy điền các thông tin dưới đây để nhà hàng {restaurant_name} " 
        "giúp quý khách đặt bàn một cách nhanh nhất nhé: \n"
        "Xin hãy chọn chi nhánh quý khách muốn đặt bàn: \n"
        "Xin hãy chọn ngày quý khách muốn đặt bàn:: \n"
        "Xin hãy chọn thời gian quý khách muốn đặt bàn: \n"
        "Xin hãy cung cấp số lượng khách: \n"
        "Xin hãy cung cấp phương thức thanh toán: \n"
        "Xin hãy cung cấp họ tên của quý khách: \n"
        "Xin hãy cung cấp số điện thoại của quý khách: \n"
        "Xin hãy cung cấp email của quý khách (tuỳ chọn): \n"
    ).format(restaurant_name=state['restaurant_info'].get('name', ''))
    
    
    booking_message = AIMessage(content=request.strip())
    
    # Cập nhật state với tin nhắn yêu cầu bằng add_messages
    state["messages"] = add_messages(state["messages"], [booking_message])
    return state

def get_user_booking_information_node(state: BookingState):
    booking_info = interrupt(None)

    try:
        # Kiểm tra các trường cần thiết
        if not all(key in booking_info for key in ["branch_id", "reservation_date", "reservation_time", "party_size",
                                                   "full_name", "phone_number", "email"]):
            raise ValueError("JSON thiếu các trường cần thiết")
        
        parse_reservation_date = datetime.strptime(booking_info["reservation_date"], "%d/%m/%Y")
        
        # Lưu thông tin đặt bàn vào state
        state["booking_info"] = {
            "branch_id": int(booking_info["branch_id"]),  # Chuyển branch thành chuỗi (vì input là số)
            "reservation_date": parse_reservation_date,
            "reservation_time": booking_info["reservation_time"],
            "party_size": int(booking_info["party_size"]),  # Đảm bảo là số nguyên
            "full_name": booking_info["full_name"],
            "phone_number": booking_info["phone_number"],
            "email": booking_info.get("email", "")
        }
        
    except (json.JSONDecodeError, ValueError):
        raise ValueError("Lỗi khi trích xuất thông tin khách hàng")

    user_request = json.dumps(booking_info, ensure_ascii=False)
    state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_request)])
    state["user_input"] = user_request

    return state

def check_availble_table_node(state: BookingState):
    table_found = find_available_table(state)
    
    if table_found is None:
        state["table_available"] = False
    else:
        state["booking_info"]["table_id"] = table_found.table_id
        state["booking_info"]["table_number"] = table_found.table_number
        state["booking_info"]["table_capacity"] = table_found.capacity
        state["table_available"] = True
        
    return state

def booking_confirmation_node(state: BookingState):
    branch_id = state['booking_info'].get('branch_id', None)
    branch_address = None
    
    if branch_id is not None:
        for branch in state["restaurant_branches"]:
            if branch["branch_id"] == branch_id:
                branch_address = branch["address"]
                break
    
    confirmation = (
        "Thông tin đặt bàn đã được ghi nhận:\n"
        f"- Chi nhánh: {branch_address or 'Không xác định'}\n"
        f"- Ngày: {state["booking_info"]["reservation_date"].strftime("%d/%m/%Y") or 'Không xác định'}\n"
        f"- Giờ: {state['booking_info']['reservation_time'] or 'Không xác định'}\n"
        f"- Số người: {state['booking_info']['party_size'] or 'Không xác định'}\n"
        f"- Số bàn: {state["booking_info"]["table_number"] or 'Không xác định'}\n"
        f"- Số lượng chỗ ngồi của bàn: {state["booking_info"]["table_capacity"] or 'Không xác định'}\n"
        "\n"
        f"- Họ và tên: {state["booking_info"]["full_name"] or "Không xác định"}\n"
        f"- Số điện thoại: {state["booking_info"]["phone_number"] or "Không xác định"}\n"
        f"- Email: {state["booking_info"]["email"] or ""}\n"
        "\n\n"
        "Quý khách vui lòng kiểm tra lại và xác nhận thông tin đặt bàn trên.\n"
        f"Ngoài ra, quý khách hãy vui lòng để nhà hàng {state["restaurant_info"]["name"]} " 
        "lưu lại thông tin cá nhân của quý khách bao gồm họ tên, số điện thoại và email (nếu có) của quý khách "
        "để phục vụ cho việc đặt bàn.\n"
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=confirmation)])
    
    return state

def get_user_confirmation_booking_node(state: BookingState):
    user_response = interrupt(None)
    
    if user_response != "YES" and user_response != "NO":
        raise ValueError("Invalid user response!")
    
    state["user_input"] = user_response
    state["intent"] = user_response
    return state

def add_customer_node(state: BookingState):
    customer = check_exist_customer_by_phone_number(state)
    state["new_customer"] = False
    
    # Customer does not exist
    if customer is None:
        customer = add_customer(state)
        state["new_customer"] = True
        
    state["customer_id"] = customer.customer_id
        
    return state

def welcome_new_customer_node(state: BookingState):
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "quý khách")
    text = (
        f"Chào mừng quý khách {customer_name} "
        f"đến với nhà hàng {restaurant_name}.\n"
        "Hệ thống nhà hàng vừa tạo tài khoản mới cho quý khách dựa vào các thông tin được cung cấp.\n"
        "Quý khách hãy sử dụng số điện thoại này để thay đổi thông tin hoặc huỷ đặt bàn.\n"
        "Nếu quý khách có thắc mắc liên quan đến thông tin đặt bàn, hãy liên hệ với nhà hàng [Tên nhà hàng] "
        "và sử dụng số điện thoại này để chúng tôi giải đáp thắc mắc của quý khách một cách nhanh nhất.\n"
        "\n"
        "Ngay sau đây, hệ thống sẽ tiến hành đặt bàn cho quý khách. Xin quý khách hãy vui lòng chờ trong giây lát."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def welcome_old_customer_node(state: BookingState):
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "quý khách")
    text = (
        f"Chào mừng quý khách {customer_name} đã quay trở lại nhà hàng {restaurant_name}.\n"
        "Nhà hàng của chúng tôi rất vui khi quý khách đã tiếp tục đặt bàn tại nhà hàng.\n"
        "\n"
        "Ngay sau đây, hệ thống sẽ tiến hành đặt bàn cho quý khách. Xin quý khách hãy vui lòng chờ trong giây lát."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def add_reservation_node(state: BookingState):
    reservation = add_reservation(state)
    
    if reservation:
        state["reservation_successful"] = True
    else:
        state["reservation_successful"] = False
    
    return state
    
def notify_reservation_successful_node(state: BookingState):
    text = get_notify_reservation_successful(state)
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def apologize_customer_node(state: BookingState):
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "quý khách")
    
    text = (
        f"Chúng tôi chân thành xin lỗi quý khách {customer_name} vì "
        f"hệ thống đặt bàn của nhà hàng {restaurant_name} đã đặt bàn không thành công.\n"
        "Quý khách xin hãy vui lòng thực hiện lại quy trình.\n"
        "Chúng tôi một lần nữa xin lỗi quý khách vì sự bất tiện này."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def suggest_alternative_node(state: BookingState):
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "quý khách")
    reservation_time = state["booking_info"].get("reservation_time", "quý khách đã đặt")
    
    text = (
        f"Chúng tôi chân thành xin lỗi quý khách {customer_name} vì "
        f"nhà hàng {restaurant_name} hiện không còn bàn phù hợp vào lúc {reservation_time} "
        "để đáp ứng được nhu cầu của quý khách.\n"
        "Quý khách có muốn chọn giờ đặt bàn khác không."
    )
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state

def get_customer_answer_for_suggestion_node(state: BookingState):
    user_answer = interrupt(None)
    intent = classify_intent_for_suggestion(user_answer)
    
    state["user_input"] = user_answer
    state["intent"] = intent
    state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_answer)])
    return state

def meet_again_node(state: BookingState):
    text = get_meet_again_text(state)
    
    state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
    return state