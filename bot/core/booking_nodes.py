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

import os
from langchain.schema import AIMessage, HumanMessage

RESTAURANT_NAME = os.getenv("RESTAURANT_NAME")

class BookingDialogue:
    def __init__(self):
        self.restaurant_name = RESTAURANT_NAME
        self.graph_function = GraphFunction()
        self.chain = BookingChain()

    def get_salutation(self, state: BookingState):
        customer_name = state.get("customer_name", "")
        check_salutation = state["salutation"]
        salutation = customer_name if check_salutation is None else f"{check_salutation.capitalize()}"
        return customer_name, check_salutation, salutation

    def prepare_booking_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        first_sentence = f"Cảm ơn {salutation} {customer_name}" if check_salutation is not None else f"Cảm ơn {customer_name}"
        
        text = (
            f"{first_sentence} đã quan tâm đến nhà hàng {self.restaurant_name}. "
            f"Để chúng tôi chuẩn bị tốt nhất cho việc đón tiếp, rất mong {salutation} cho phép cung cấp một vài thông tin cần thiết ạ."
        ).strip()
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state

    def ask_phone_number_node(self, state: BookingState) -> BookingState:
        _, _, salutation = self.get_salutation(state)
        
        text = (
            f"Đầu tiên, để hoàn tất việc giữ bàn và tiện xác nhận khi {salutation} đến dùng bữa, "
            f"nhà hàng {self.restaurant_name} xin phép được hỏi số điện thoại của {salutation} ạ."
        ).strip()
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state

    def get_user_phone_number_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state
    
    def ask_phone_again_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Rất xin lỗi {salutation}, nhưng có vẻ số điện thoại {salutation} vừa cung cấp chưa đúng định dạng. "
            f"{salutation} vui lòng kiểm tra và cung cấp lại giúp nhà hàng nhé.\n"
            f"🌟 Lưu ý: Số điện thoại hợp lệ gồm 10 chữ số và bắt đầu bằng số 0 ạ."
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def number_requireded_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, nhà hàng hoàn toàn tôn trọng quyền riêng tư của Quý khách.\n"
            f"Tuy nhiên, để đảm bảo việc giữ bàn và hỗ trợ xác nhận thông tin khi đến dùng bữa, "
            f"việc cung cấp số điện thoại liên hệ là rất cần thiết ạ.\n"
            f"Rất mong {salutation} thông cảm và cân nhắc giúp nhà hàng trong trường hợp này ạ. 💖"
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def add_phone_number_node(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        phone_number = self.graph_function.extract_phone_number(user_input)
        print(f"> Số điện thoại đã trích xuất: {phone_number}")
        state["customer_phone_number"] = phone_number
        
        try:
            customer = self.graph_function.add_customer_phone_number(state=state)
            print(f"> Thêm số điện thoại thành công")
        except Exception as e:
            raise(f"Error add phone number: {e}")
        
        return state
    
    def ask_booking_info_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation} vui lòng cho biết thời gian muốn đặt bàn (ngày và giờ cụ thể), "
            f"cũng như số lượng người sẽ dùng bữa cùng ạ."
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def get_booking_info_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        salutation = state["salutation"]
        last_question = state["messages"][-1].content
        
        print(f"> Câu hỏi của bot là: {last_question}")
        
        extract_data = self.chain.extract_booking_info().invoke({
            "current_date": datetime.today().strftime('%Y-%m-%d'),
            "salutation":salutation,
            "user_input": user_input,
            "last_question": last_question
        })
        result = extract_data.content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
        print(result)
        json_data = json.loads(result)
        
        state["date"] = json_data.get("date", None) if state["date"] is None else state["date"]
        state["time"] = json_data.get("time", None) if state["time"] is None else state["time"]
        state["people"] = json_data.get("people", None) if state["people"] is None else state["people"]
        state["note"] = json_data.get("note", None) if state["note"] is None else state["note"]
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state
    
    def ask_for_correct_information_node(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        inappropriate_information = state["inappropriate_information"]
        missing_information = state["missing_information"]
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        question = self.chain.ask_correct_booking_info().invoke({
            "user_input": user_input,
            "missing_information": missing_information,
            "inappropriate_information": inappropriate_information,
            "salutation": salutation
        })
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=question.content)])
        return state
    
    def get_available_table_node(self, state: BookingState) -> BookingState:
        available_table = self.graph_function.find_available_table(state)
        
        state["table_id"] = available_table.table_id
        state["table_number"] = available_table.table_number
        return state

    def announce_no_available_table_node(self, state: BookingState) -> BookingState:
        _, _, salutation = self.get_salutation(state)
        reservation_date = datetime.strptime(state["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        reservation_time = state["time"]
        
        text = (
            f"Dạ {salutation}, rất tiếc là vào lúc {reservation_time} ngày {reservation_date}, "
            f"nhà hàng {self.restaurant_name} hiện không còn bàn phù hợp với số lượng khách đặt bàn ạ. "
            f"{salutation} có muốn chọn một khung giờ hoặc ngày khác để đặt bàn không ạ?"
        ).strip()

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def confirm_continue_booking_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state
    
    def end_booking_with_thanks(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Nhà hàng rất tiếc vì không thể phục vụ {salutation} vào thời gian mong muốn. " 
            f"Rất cảm ơn {salutation} đã quan tâm đến nhà hàng {self.restaurant_name}. "
            f"Hy vọng sẽ được đón tiếp {salutation} vào dịp gần nhất ạ.\n"
            "Kính chúc {salutation} một ngày thật vui vẻ và nhiều sức khỏe!"
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def ask_again_booking_info_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, không biết {salutation} muốn đổi sang khung giờ hoặc ngày nào khác ạ? "
            f"Nhà hàng sẽ kiểm tra và phản hồi ngay để hỗ trợ quý khách tốt nhất ạ."
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def get_booking_again_info_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        extract_data = self.chain.extract_booking_info().invoke({
            "current_date": datetime.today().strftime('%Y-%m-%d'),
            "salutation": salutation,
            "user_input": user_input
        })
        
        result = extract_data.content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
        print(f"> Khách muốn đặt lại với thông tin {result}")
        json_data = json.loads(result)
        
        state["date"] = json_data.get("date", None) if json_data["date"] is not None else state["date"]
        state["time"] = json_data.get("time", None) if json_data["time"] is not None else state["time"]
        state["people"] = json_data.get("people", None) if json_data["people"] is not None else state["people"]
        state["note"] = json_data.get("note", None) if json_data["note"] is not None else state["note"]
        
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state
    
    def extract_booking_info_node(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        extract_data = self.chain.extract_booking_info().invoke({
            "current_date": datetime.today().strftime('%Y-%m-%d'),
            "salutation":salutation,
            "user_input": user_input
        })
        result = extract_data.content.replace("```json\n", "").replace("\n```", "").replace("\n", "")
        print(f"> Khách muốn đặt lại với thông tin {result}")
        json_data = json.loads(result)
        
        state["date"] = json_data.get("date", None) if json_data["date"] is not None else state["date"]
        state["time"] = json_data.get("time", None) if json_data["time"] is not None else state["time"]
        state["people"] = json_data.get("people", None) if json_data["people"] is not None else state["people"]
        state["note"] = json_data.get("note", None) if json_data["note"] is not None else state["note"]
        
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state

    def confirm_booking_node(self, state: BookingState) -> BookingState:
        reservation_date = datetime.strptime(state["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        time = state["time"]
        people = state["people"]
        note = state["note"] if state["note"] != "" else "Không có ghi chú"
        table_number = state["table_number"]
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, nhà hàng xin phép được xác nhận lại thông tin đặt bàn của {salutation} như sau:\n"
            f"- Bàn số: {table_number}\n"
            f"- Thời gian: {time}, ngày {reservation_date}\n"
            f"- Số lượng khách: {people} người\n"
            f"- Ghi chú: {note}\n"
            f"{salutation} vui lòng kiểm tra giúp nhà hàng xem thông tin trên đã chính xác chưa ạ?"
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state

    def get_confirm_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state

    def ask_edit_booking_info_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ {salutation}, không biết {salutation} cần điều chỉnh thông tin nào trong đơn đặt bàn ạ? "
            f"Nhà hàng sẽ kiểm tra và phản hồi sớm nhất để hỗ trợ quý khách chu đáo nhất ạ."
        )

        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def goodbye_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        now = datetime.now()

        # Xác định thời gian chào theo giờ hiện tại
        greeting_time = "một ngày" if 5 <= now.hour < 18 else "một đêm"

        text = (
            f"Dạ, nhà hàng xin cảm ơn {salutation} đã quan tâm đến dịch vụ của chúng tôi. "
            f"Rất mong sẽ có cơ hội được phục vụ {salutation} vào dịp khác. "
            f"Kính chúc {salutation} {greeting_time} thật nhiều niềm vui và sức khỏe ạ!"
        )
        
        state["state"] = "END"
        customer = self.graph_function.add_state(state["customer_id"], state["state"])
        if customer:
            print("> Thêm state END thành công")
        else:
            print("> Thêm state END không thành công")
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state

    def add_reservation_node(self, state: BookingState) -> BookingState:
        reservation = self.graph_function.add_reservation(state)
        state["booking_successful"] = True
        
        if not reservation:
            state["booking_successful"] = False
        
        return state
        
    def thank_you_booking_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        reservation_date = datetime.strptime(state["date"], "%Y-%m-%d").strftime("%d-%m-%Y")
        time = state["time"]
        
        text = (
            f"Dạ, nhà hàng đã đặt bàn thành công và xin hẹn gặp lại {salutation} vào lúc {time} ngày {reservation_date} ạ. "
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
    
    def not_booking_successful_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        
        text = (
            f"Dạ, rất xin lỗi {salutation}, hiện tại hệ thống đang gặp sự cố nên chưa thể tiếp nhận đặt bàn. "
            f"Quý khách vui lòng thử lại sau ít phút hoặc liên hệ trực tiếp với nhà hàng để được hỗ trợ nhanh chóng hơn ạ. "
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