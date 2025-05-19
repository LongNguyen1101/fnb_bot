from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from bot.core.state import BookingState
from langgraph.types import interrupt
from datetime import datetime
import json
from bot.core.graph_function import GraphFunction
from bot.chain.booking_chain import BookingChain
from dotenv import load_dotenv
import os

load_dotenv(override=True)

RESTAURANT_NAME = os.getenv("RESTAURANT_NAME")

class CancelDialogue:
    def __init__(self):
        self.restaurant_name = RESTAURANT_NAME
        self.graph_function = GraphFunction()
        self.chain = BookingChain()
    
    def get_salutation(self, state: BookingState):
        customer_name = state.get("customer_name", "")
        check_salutation = state["salutation"]
        salutation = customer_name if check_salutation is None else f"{check_salutation.capitalize()}"
        return customer_name, check_salutation, salutation
    
    def announce_wait_to_get_reservation_cancel_node(self, state: BookingState) -> BookingState:
        # Lấy lại bên modify node
        pass
    
    def get_reservation_cancel_node(self, state: BookingState) -> BookingState:
        # Lấy lại bên modify node
        pass

    def notify_not_found_reservation_cancel_node(self, state: BookingState) -> BookingState:
        # Lấy lại bên modify node
        pass
    
    def ask_cancel_reservation_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        list_reservation = state["list_reservation"]
        print(list_reservation)
        
        question = self.chain.ask_cancel_reservation().invoke({
            "list_reservation": list_reservation,
            "salutation": salutation
        })
        
        state["modify_question"] = question.content
        state["messages"] = add_messages(state["messages"], [AIMessage(content=question.content)])
        return state
    
    
    def get_cancel_info_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        
        customer_name, check_salutation, salutation = self.get_salutation(state)
        list_reservation = state["list_reservation"]
        
        extract_data = self.chain.extract_cancel_info().invoke({
            "salutation": salutation,
            "user_input": user_input,
            "list_reservation": list_reservation
        })
        
        result = extract_data.content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
        print(f"> Khách muốn huỷ bàn với mã đặt bàn {result}")
        json_data = json.loads(result)
        state["reservation_id_chosen"] = json_data.get("reservation_id_chosen", None)
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state
    
    def ask_for_correct_cancel_node(self, state: BookingState) -> BookingState:
        # Lấy lại của modify
        pass
    
    def confirm_cancel_node(self, state: BookingState) -> BookingState:
        reservation_date = datetime.strptime(state["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        time = state["time"]
        people = state["people"]
        note = state["note"] if state["note"] != "" else "Không có ghi chú"
        reservation_id_chosen = state["reservation_id_chosen"]
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, nhà hàng đã tiếp nhận yêu cầu huỷ đặt bàn của {salutation} với thông tin sau:\n"
            f"- Mã đặt bàn: {reservation_id_chosen}\n"
            f"- Thời gian: {time}, ngày {reservation_date}\n"
            f"- Số lượng khách: {people} người\n"
            f"- Ghi chú: {note}\n"
            f"{salutation} vui lòng xác nhận lại để nhà hàng tiến hành huỷ đặt bàn ạ."
        )

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def get_confirm_cancel_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state
    
    
    def ask_edit_cancel_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, không biết {salutation} cần điều chỉnh thông tin nào ạ? "
            f"Nhà hàng sẽ kiểm tra và phản hồi sớm nhất để hỗ trợ quý khách chu đáo nhất ạ."
        )

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def end_cancel_node(self, state: BookingState) -> BookingState:
         # Lấy lại bên modify node
        pass
    
    def cancel_reservation_node(self, state: BookingState) -> BookingState:
        cancelled_reservation = self.graph_function.cancel_reservation(state)
        state["cancel_successful"] = False

        if cancelled_reservation is not None:
            state["cancel_successful"] = True

        return state
    
    def thank_you_cancel_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ, cảm ơn {salutation} đã quan tâm đến dịch vụ của nhà hàng. "
            f"Nhà hàng xin xác nhận đã huỷ đơn đặt bàn của {salutation} thành công ạ. "
            f"Nhà hàng rất tiếc vì chưa có dịp được phục vụ {salutation} lần này. "
            f"Hy vọng sẽ được chào đón {salutation} trong thời gian gần nhất. "
            f"Kính chúc {salutation} luôn nhiều sức khỏe và niềm vui!"
        )
        
        state["state"] = "END"
        customer = self.graph_function.add_state(state["customer_id"], state["state"])
        if customer:
            print("> Thêm state END thành công")
        else:
            print("> Thêm state END không thành công")

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def not_cancel_successful_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ, rất xin lỗi {salutation}, hiện tại hệ thống đang gặp sự cố nên chưa thể huỷ thông tin đặt bàn của {salutation}. "
            f"{salutation} vui lòng thử lại sau ít phút hoặc liên hệ trực tiếp với nhà hàng để được hỗ trợ nhanh chóng hơn ạ. "
            f"Rất mong {salutation} thông cảm cho sự bất tiện này!"
        )
        
        state["state"] = "END"
        customer = self.graph_function.add_state(state["customer_id"], state["state"])
        if customer:
            print("> Thêm state END thành công")
        else:
            print("> Thêm state END không thành công")
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state


# def cancel_node(state: BookingState):
#     restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    
#     text = (
#         "Quý khách vui lòng hãy cung cấp số điện thoại mà quý khách đã "
#         f"sử dụng để đặt bàn tại nhà hàng {restaurant_name}.\n"
#     )
    
#     state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
#     return state

# def return_customer_reservation_cancel_node(state: BookingState) -> BookingState:
#     list_reservations = state.get("list_reservations", None)
    
#     text = ""
#     for reservation in list_reservations:
#         try:
#             text += (
#                 f"Thông tin đặt bàn số: {reservation['reservation_id']}\n"
#                 f"Chi nhánh: {reservation['branch_id']}\n"
#                 f"Địa chỉ: {reservation['address']}\n"
#                 f"Ngày đặt: {reservation['reservation_date']}\n"
#                 f"Thời gian đặt: {reservation['reservation_time']}\n"
#                 f"Số lượng người: {reservation['party_size']}\n\n"
#             )
#         except KeyError as e:
#             text += f"Lỗi: Thiếu thông tin cho đặt bàn (thiếu key: {e})\n\n"

#     if not list_reservations:
#         text += "Không có thông tin đặt bàn nào.\n"

#     text += "Quý khách hãy sửa đổi thông tin đặt bàn theo mong muốn của quý khách."
    
#     state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
#     return state

# def get_cancel_reservation(state: BookingState) -> BookingState:
#     update_info = interrupt(None)
#     update_info = extract_modify_input_user(update_info)
#     update_info = json.loads(update_info)
#     print("update info", update_info)
    
#     try:
#         # update_info = json.loads(user_request)
#         # Kiểm tra các trường cần thiết
#         if not all(key in update_info for key in ["branch_id", "address", "reservation_date",
#                                                   "reservation_time", "party_size", "reservation_id_chosen"]):
#             raise ValueError("JSON thiếu các trường cần thiết")
        
#         parse_reservation_date = datetime.strptime(update_info["reservation_date"], "%d/%m/%Y")
        
#         # Lưu thông tin đặt bàn vào state
#         state["booking_info"] = {
#             "reservation_id_chosen": int(update_info["reservation_id_chosen"]),
#             "branch_id": int(update_info["branch_id"]),
#             "address": update_info["address"],
#             "reservation_date": parse_reservation_date,
#             "reservation_time": update_info["reservation_time"],
#             "party_size": int(update_info["party_size"])
#         }
        
#     except (json.JSONDecodeError, ValueError):
#         raise ValueError("Lỗi khi trích xuất thông tin khách hàng")

#     user_request = json.dumps(update_info, ensure_ascii=False)
#     state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_request)])
#     state["user_input"] = user_request

#     return state

# def warning_cancel(state: BookingState) -> BookingState:
#     customer_name = state["booking_info"].get("full_name", "")
    
#     parse_reservation_date = state["booking_info"]["reservation_date"].strftime('%d/%m/%Y')
    
#     text = (
#         f"Quý khách {customer_name} có chắc chắn muốn huỷ thông tin đặt bàn dưới đây không:\n"
#         f"- Địa chỉ chi nhánh: {state["booking_info"]["address"]}\n"
#         f"- Ngày đặt bàn: {parse_reservation_date}\n"
#         f"- Thòi gian đặt bàn: {state["booking_info"]["reservation_time"]}\n"
#         f"- Số lượng người: {state["booking_info"]["party_size"]}\n"
#         "Xin quý khách cân nhắc thật kỹ trước khi quyết định huỷ đặt bàn."
#     ).strip()
    
#     state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
#     return state

# def get_confirm_cancel_node(state: BookingState) -> BookingState:
#     user_response = interrupt(None)
    
#     if user_response != "YES" and user_response != "NO":
#         raise ValueError("Invalid user response!")
    
#     state["user_input"] = user_response
#     state["intent"] = user_response
#     state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_response)])
#     return state

# def update_cancel_node(state: BookingState) -> BookingState:
#     cancelled_reservation = cancel_reservation(state)
#     state["cancel_successful"] = False
    
#     if cancelled_reservation is not None:
#         state["cancel_successful"] = True
    
#     return state

# def thank_you_for_not_cancel(state: BookingState) -> BookingState:
#     restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
#     customer_name = state["booking_info"].get("full_name", "")
#     parse_reservation_date = state["booking_info"]["reservation_date"].strftime('%d/%m/%Y')
    
#     text = (
#         f"Xin chân thành cảm ơn quý khách {customer_name} đã suy nghĩ lại và quyết định không huỷ bàn "
#         f"tại nhà hàng {restaurant_name}.\n"
#         f"Nhà hàng chúng tôi rất mong chờ được gặp quý khách vào {parse_reservation_date}"
#     )
    
#     state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
#     return state

# def notify_cancel_successful_node(state: BookingState) -> BookingState:
#     restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
#     customer_name = state["booking_info"].get("full_name", "")
#     reservation_time = state["booking_info"].get("reservation_time", "thời gian đã đặt")
#     parse_reservation_date = state["booking_info"]["reservation_date"].strftime('%d/%m/%Y')
    
#     text = (
#         f"Xin thông báo quý khách {customer_name} đã huỷ đặt bàn thành công.\n"
#         f"Nhà hàng {restaurant_name} rất tiếc vì không thể phục vụ được quý khách vào lúc "
#         f"{reservation_time}, ngày {parse_reservation_date}.\n"
#         "Chúng tôi mong chờ được phục vụ quý khách một ngày không xa.\n"
#         "Trong quá trình đặt bàn, nếu quý khách có bất kỳ điều gì không hài lòng "
#         "thì hãy liên hệ với chúng tôi.\n"
#         f"Nhà hàng {restaurant_name} xin cảm ơn vì đã được phục vụ quý khách {customer_name}."
#     )
    
#     state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
#     return state

# def notify_cancel_unsuccessful_node(state: BookingState) -> BookingState:
#     restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
#     customer_name = state["booking_info"].get("full_name", "")
    
#     text = (
#         f"Nhà hàng {restaurant_name} chân thành xin lỗi quý khách {customer_name} vì không thể tìm được "
#         "thông tin đặt bàn của quý khách.\n"
#         "Xin quý khách vui lòng chọn lại thông tin đặt bàn mà quý khách muốn huỷ một lần nữa.\n"
#     )
    
#     state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])

#     return state