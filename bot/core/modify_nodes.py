from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from bot.core.state import BookingState
from langgraph.types import interrupt
import json
from datetime import datetime
from bot.core.graph_function import GraphFunction
from bot.chain.booking_chain import BookingChain
from dotenv import load_dotenv
import os

load_dotenv(override=True)

RESTAURANT_NAME = os.getenv("RESTAURANT_NAME")

class ModifyDialogue:
    def __init__(self):
        self.restaurant_name = RESTAURANT_NAME
        self.graph_function = GraphFunction()
        self.chain = BookingChain()

    def get_salutation(self, state: BookingState):
        customer_name = state.get("customer_name", "")
        check_salutation = state["salutation"]
        salutation = customer_name if check_salutation is None else f"{check_salutation.capitalize()}"
        return customer_name, check_salutation, salutation
    
    def announce_wait_to_get_reservation_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ, xin phép {salutation} vui lòng chờ một chút để nhà hàng kiểm tra lại thông tin đặt bàn giúp {salutation} ạ."
        )

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def get_reservation_node(self, state: BookingState) -> BookingState:
        list_reservation = self.graph_function.get_reservations_of_customer(state)
        print(f"> Tìm thấy danh sách đặt bàn: {list_reservation}")
        
        state["list_reservation"] = list_reservation
        return state
    
    def notify_not_found_reservation_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ, hiện tại nhà hàng chưa ghi nhận thông tin đặt bàn nào từ {salutation} ạ. "
            f"Không biết {salutation} có mong muốn tiến hành đặt bàn ngay bây giờ không ạ?"
        )

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def ask_modify_reservation_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        list_reservation = state["list_reservation"]
        print(list_reservation)
        
        question = self.chain.ask_modify_reservation().invoke({
            "list_reservation": list_reservation,
            "salutation": salutation
        })
        
        state["modify_question"] = question.content
        state["messages"] = add_messages(state["messages"], [AIMessage(content=question.content)])
        return state
    
    def get_modify_info_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        
        customer_name, check_salutation, salutation = self.get_salutation(state)
        list_reservation = state["list_reservation"]
        
        extract_data = self.chain.extract_modify_info().invoke({
            "current_date": datetime.today().strftime('%Y-%m-%d'),
            "salutation": salutation,
            "user_input": user_input,
            "list_reservation": list_reservation
        })
        
        result = extract_data.content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
        print(f"> Khách muốn đặt lại với thông tin {result}")
        json_data = json.loads(result)
        
        state["table_id"] = json_data.get("table_id", None)
        state["reservation_id_chosen"] = json_data.get("reservation_id_chosen", None)
        state["date"] = json_data.get("date", None)
        state["time"] = json_data.get("time", None)
        state["people"] = json_data.get("people", None)
        state["note"] = json_data.get("note", None)
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state

    def ask_for_correct_modify_node(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        inappropriate_information = state["inappropriate_information"]
        missing_information = []
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        question = self.chain.ask_correct_booking_info().invoke({
            "user_input": user_input,
            "missing_information": missing_information,
            "inappropriate_information": inappropriate_information,
            "salutation": salutation
        })
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=question.content)])
        return state

        
    # def get_available_table_modify_node
    # def announce_no_available_table_modify_node
    # def confirm_continue_modify_node
    # ---> Sử dụng lại của bookinh nodes
    
    def end_modify_with_thanks(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ vâng, nhà hàng đã ghi nhận giữ nguyên thông tin đặt bàn ban đầu của {salutation} ạ. "
            f"Cảm ơn {salutation} rất nhiều! "
            f"Nếu {salutation} cần hỗ trợ thêm bất kỳ điều gì khác, cứ nhắn cho nhà hàng bất cứ lúc nào nhé!"
        )

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def ask_modify_again_info_node(self, state: BookingState) -> BookingState:
        ustomer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, không biết {salutation} muốn thay đổi thông tin nào khác ạ? "
            f"Nhà hàng sẽ kiểm tra và phản hồi ngay để hỗ trợ quý khách tốt nhất ạ."
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def get_modify_again_info_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        
        customer_name, check_salutation, salutation = self.get_salutation(state)
        list_reservation = state["list_reservation"]
        reservation_id_chosen = state["reservation_id_chosen"]
        date = state["date"]
        time = state["time"]
        people = state["people"]
        note = state["note"]
        
        extract_data = self.chain.extract_modify_again_info().invoke({
            "user_input": user_input,
            "list_reservation": list_reservation,
            "current_date": datetime.today().strftime('%Y-%m-%d'),
            "salutation": salutation,
            "reservation_id_chosen": reservation_id_chosen,
            "date": date,
            "time": time,
            "people": people,
            "note": note
        })
        
        result = extract_data.content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
        print(f"> Khách muốn đặt lại với thông tin {result}")
        json_data = json.loads(result)
        
        state["reservation_id_chosen"] = json_data.get("reservation_id_chosen", None)
        state["date"] = json_data.get("date", None)
        state["time"] = json_data.get("time", None)
        state["people"] = json_data.get("people", None)
        state["note"] = json_data.get("note", None)
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state

    def extract_modify_info_node(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        customer_name, check_salutation, salutation = self.get_salutation(state)
        list_reservation = state["list_reservation"]
        reservation_id_chosen = state["reservation_id_chosen"]
        date = state["date"]
        time = state["time"]
        people = state["people"]
        note = state["note"]
        
        extract_data = self.chain.extract_modify_again_info().invoke({
            "user_input": user_input,
            "list_reservation": list_reservation,
            "current_date": datetime.today().strftime('%Y-%m-%d'),
            "salutation": salutation,
            "reservation_id_chosen": reservation_id_chosen,
            "date": date,
            "time": time,
            "people": people,
            "note": note
        })
        
        result = extract_data.content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
        print(f"> Khách muốn đặt lại với thông tin {result}")
        json_data = json.loads(result)
        
        state["reservation_id_chosen"] = json_data.get("reservation_id_chosen", None)
        state["date"] = json_data.get("date", None)
        state["time"] = json_data.get("time", None)
        state["people"] = json_data.get("people", None)
        state["note"] = json_data.get("note", None)
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state

    def confirm_modify_node(self, state: BookingState) -> BookingState:
        reservation_date = datetime.strptime(state["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        time = state["time"]
        people = state["people"]
        note = state["note"] if state["note"] != "" else "Không có ghi chú"
        reservation_id_chosen = state["reservation_id_chosen"]
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, nhà hàng xin phép được xác nhận lại thông tin đặt bàn sau khi thay đổi của {salutation} như sau:\n"
            f"- Mã đặt bàn: {reservation_id_chosen}\n"
            f"- Thời gian: {time}, ngày {reservation_date}\n"
            f"- Số lượng khách: {people} người\n"
            f"- Ghi chú: {note}\n"
            f"{salutation} vui lòng kiểm tra giúp nhà hàng xem thông tin trên đã chính xác chưa ạ?"
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def get_confirm_modify_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state
    
    def ask_edit_modify_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, không biết {salutation} cần điều chỉnh thông tin nào trong đơn đặt bàn ạ? "
            f"Nhà hàng sẽ kiểm tra và phản hồi sớm nhất để hỗ trợ quý khách chu đáo nhất ạ."
        )

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def end_modify_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        now = datetime.now()

        # Xác định thời gian chào theo giờ hiện tại
        greeting_time = "một ngày" if 5 <= now.hour < 18 else "một đêm"

        text = (
            f"Dạ vâng, nhà hàng đã ghi nhận mong muốn giữ nguyên thông tin đặt bàn ban đầu của {salutation} ạ. "
            f"Cảm ơn {salutation} đã dành thời gian! "
            f"{salutation} cần điều chỉnh gì thêm trong thời gian tới, nhà hàng luôn sẵn sàng hỗ trợ ạ. "
            f"Kính chúc {salutation} {greeting_time} thật nhiều niềm vui và sức khỏe!"
        )
        
        state["state"] = "END"
        customer = self.graph_function.add_state(state["customer_id"], state["state"])
        if customer:
            print("> Thêm state END thành công")
        else:
            print("> Thêm state END không thành công")

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def update_reservation_node(self, state: BookingState) -> BookingState:
        updated_reservation = self.graph_function.update_reservation_info(state)
        state["modify_successful"] = True
        
        if not updated_reservation:
            state["modify_successful"] = False
        
        return state
    
    def thank_you_modify_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        reservation_date = datetime.strptime(state["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        time = state["time"]
        
        text = (
            f"Dạ, nhà hàng đã thay đổi thông tin đặt bàn thành công và xin hẹn gặp lại {salutation} vào lúc {time} ngày {reservation_date} ạ. "
            f"Rất mong được đón tiếp và phục vụ {salutation} một cách chu đáo nhất. "
            f"Nếu có thay đổi nào về thời gian hoặc số lượng khách, {salutation} vui lòng báo lại giúp nhà hàng nhé!"
        )
        
        state["state"] = "END"
        customer = self.graph_function.add_state(state["customer_id"], state["state"])
        if customer:
            print("> Thêm state END thành công")
        else:
            print("> Thêm state END không thành công")
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def not_modify_successful_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ, rất xin lỗi {salutation}, hiện tại hệ thống đang gặp sự cố nên chưa thay đổi thông tin đặt bàn của {salutation}. "
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