from bot.core.state import BookingState
from bot.core.graph_function import GraphFunction
from bot.chain.booking_chain import BookingChain
from langgraph.graph import END
from typing import List

# ROUTER

class GraphRouter():
    def __init__(self):
        self.graph_function = GraphFunction()
        self.chain = BookingChain()
        
    def first_intent_router(self, state: BookingState) -> BookingState:
        intent = None
        next_node = "booking"
        
        if state["intent"] is None:
            print("> Không thấy gửi intent trong body")
            user_input = state["user_input"]
            print(f"> Khách nhắn: {user_input}")
            
            check_intent = self.chain.check_first_intent().invoke(user_input)
            intent = check_intent.content
            state["intent"] = intent
        else:
            print("> Thấy gửi intent trong body")
            intent = state["intent"]
        
        print(f"> Khách muốn: {intent}")
        print(f">>>> intent: {intent}")
        
        if intent == "booking":
            next_node = "booking"
        elif intent == "modify":
            next_node = "modify"
        elif intent == "cancel":
            next_node = "cancel"
        
        state["next_node"] = next_node
        return state
    
    def check_salutation_router(self, state: BookingState) -> BookingState:
        salutaion = state["salutation"]
        next_node = "no"
        
        if salutaion is not None:
            next_node = "yes"
            
        state["next_node"] = next_node
        return state
    
    def check_exists_phone_number(self, state: BookingState) -> BookingState:
        next_node = "yes"
        if state["customer_phone_number"] is None:
            print(f"> Không thấy số điện thoại khách hàng -> hỏi khách")
            next_node = "no"
        
        state["next_node"] = next_node
        return state
    
    def check_user_phone_router(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        result = self.graph_function.check_user_phone(user_input=user_input)
        print(f"> Phân loại câu trả lời của khách: {result}")
        
        next_node = END
        if result == "wrong_number":
            next_node = "wrong_number"
        elif result == "need_number":
            next_node = "need_number"
        elif result == "not_relevant":
            next_node = "not_relevant"
        elif result == "normal":
            next_node = "normal"
        
        state["next_node"] = next_node
        return state
        
        
    def check_user_booking_router(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        next_node = "normal"
        inappropriate_information_note = []
        missing_information = []
        last_question = state["messages"][-2].content
        print(f"> Câu hỏi của bot là: {last_question}")
        
        check_booking_relatedness = self.chain.check_booking_relatedness().invoke({
            "user_input": user_input,
            "last_question": last_question
        }).content
        
        if check_booking_relatedness == "no":
            next_node = "not_relevant"
        else:
            inappropriate_information_note = self.graph_function.check_inappropriate_information(state=state)
            missing_information = self.graph_function.check_missing_information(state=state)

            if len(inappropriate_information_note) > 0:
                print(f"Thông tin đặt bàn không hợp lệ: {inappropriate_information_note}")
                next_node = "inappropriate_information"

            if len(missing_information) > 0:
                print(f"Thông tin đặt bàn bị thiếu: {missing_information}")
                next_node = "inappropriate_information"
                
        print(f"> Node tiếp theo là: {next_node}")
        
        state["next_node"] = next_node
        state["inappropriate_information"] = inappropriate_information_note
        state["missing_information"] = missing_information
        return state
    
    def check_available_table_router(self, state: BookingState) -> BookingState:
        table_id = state["table_id"]
        next_node = "yes"
        
        if table_id is None:
            print("> Không tìm thấy bàn")
            next_node = "no"
        else:
            print(f"> Đã tìm thấy bàn: table_id {table_id}")

        state["next_node"] = next_node
        return state
    
    def check_continue_booking_router(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        intent = self.chain.classify_continue_booking().invoke(user_input).content
        next_node = "no_continue"
        
        if intent == "continue_without_info":
            next_node = "continue_without_info"
        elif intent == "no_continue":
            next_node = "no_continue"
        elif intent == "continue_with_info":
            next_node = "continue_with_info"
        
        state["next_node"] = next_node
        return state
    
    def check_user_confirm_router(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        intent = self.chain.confirm_reservation_intent_classification().invoke(user_input).content
        print(f"> Khi xác nhận đặt bàn, khách muốn: {intent}")
        next_node = "confirm"
        
        if intent == "confirm":
            next_node = "confirm"
        elif intent == "need_edit":
            next_node = "need_edit"
        elif intent == "exit":
            next_node = "exit"
        elif intent == "not_relevant":
            next_node = "not_relevant"
        
        state["next_node"] = next_node
        return state
    
    def booking_successful_router(self, state: BookingState) -> BookingState:
        booking_successful = state["booking_successful"]
        next_node = "successful"
        
        if booking_successful is False:
            next_node = "unsuccessful"
        
        state["next_node"] = next_node
        return state
    
    def check_quantity_reservation_router(self, state: BookingState) -> BookingState:
        list_reservation = state["list_reservation"]
        print(f"> Số lượng đơn đặt bàn: {len(list_reservation)}")
        next_node = "no_reservation"
        
        if len(list_reservation) == 0:
            next_node = "no_reservation"
        elif len(list_reservation) == 1:
            state["reservation_id_chosen"] = list_reservation[0]["reservation_id"]
            next_node = "reservation"
        elif len(list_reservation) > 1:
            next_node = "reservation"
        
        state["next_node"] = next_node
        return state
    
    def check_user_modify_router(self, state: BookingState) -> BookingState:
        next_node = "normal"
        inappropriate_information_note = self.graph_function.check_inappropriate_information(state)
        list_reservation_idx = [reservation["reservation_id"] for reservation in state["list_reservation"]]
        
        reservation_id_chosen = state["reservation_id_chosen"] or list_reservation_idx[0]
        if reservation_id_chosen not in list_reservation_idx:
            inappropriate_information_note.append("Chọn sai mã đặt bàn. Đặt lại")
        
        if len(inappropriate_information_note) > 0:
            print(f"> Khách đặt sai thông tin: {inappropriate_information_note}")
            state["inappropriate_information"] = inappropriate_information_note
            next_node = "inappropriate_information"
        else:
            print(f"> Thông tin đặt lại hợp lệ")
        
        state["next_node"] = next_node
        return state
        
    def check_party_size_router(self, state: BookingState) -> BookingState:
        next_node = "smaller"
        people = state["people"]
        
        capacity = self.graph_function.get_capacity_in_reservation(state)[0]
        print(f"> Số khách {people}")
        print(f"> Sức chứa của bàn {capacity}")
        
        if people <= capacity:
            next_node = "smaller"
            print(f"> Số khách ({people}) nhỏ hơn hoặc bằng sức chứa của bàn ({capacity})")
        else:
            next_node = "greater"
            print(f"> Số khách ({people}) lớn hơn sức chứa của bàn ({capacity})")
        
        state["next_node"] = next_node
        return state
        
    def check_user_confirm_modify_router(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        intent = self.chain.confirm_reservation_intent_classification().invoke(user_input).content
        print(f"> Khi xác nhận thay đổi đặt bàn, khách muốn: {intent}")
        next_node = "confirm"
        
        if intent == "confirm":
            next_node = "confirm"
        elif intent == "need_edit":
            next_node = "need_edit"
        elif intent == "exit":
            next_node = "exit"
        elif intent == "not_relevant":
            next_node = "not_relevant"
        
        state["next_node"] = next_node
        return state
    
    def modify_successful_router(self, state: BookingState) -> BookingState:
        modify_successful = state["modify_successful"]
        next_node = "successful"
        
        if modify_successful is False:
            next_node = "unsuccessful"
        
        state["next_node"] = next_node
        return state
    
    def check_quantity_reservation_cancel_router(self, state: BookingState) -> BookingState:
        # Lấy lại router của modify node
        pass
    
    def check_user_cancel_router(self, state: BookingState) -> BookingState:
        inappropriate_information_note = []
        next_node = "normal"
        list_reservation_idx = [reservation["reservation_id"] for reservation in state["list_reservation"]]
        
        reservation_id_chosen = state["reservation_id_chosen"] or list_reservation_idx[0]
        if reservation_id_chosen not in list_reservation_idx:
            inappropriate_information_note.append("Chọn sai mã đặt bàn. Đặt lại")
            next_node = "inappropriate_information"
        else:
            reservation = self.graph_function.get_reservation_info(state)
            if reservation is not None:
                print(f"> Tìm thấy đơn đặt bàn")
                next_node = "normal"
                state["table_id"] = reservation.table_id
                state["date"] = reservation.reservation_date.strftime("%Y-%m-%d")
                state["time"] = reservation.reservation_time.strftime("%H:%M")
                state["people"] = reservation.party_size
                state["note"] = reservation.note
            else:
                print(f"> Không tìm thấy đơn đặt bàn")
                inappropriate_information_note.append("Không tìm thấy đơn đặt bàn. Đặt lại")
                next_node = "inappropriate_information"
        
        state["inappropriate_information"] = inappropriate_information_note
        state["next_node"] = next_node
        return state
    
    def check_user_confirm_cancel_router(self, state: BookingState) -> BookingState:
        user_input = state["user_input"]
        intent = self.chain.confirm_reservation_intent_classification().invoke(user_input).content
        print(f"> Khi xác nhận huỷ đặt bàn, khách muốn: {intent}")
        next_node = "confirm"
        
        if intent == "confirm":
            next_node = "confirm"
        elif intent == "need_edit":
            next_node = "need_edit"
        elif intent == "exit":
            next_node = "exit"
        elif intent == "not_relevant":
            next_node = "not_relevant"
        
        state["next_node"] = next_node
        return state
    
    def cancel_successful_router(self, state: BookingState) -> BookingState:
        cancel_successful = state.get("cancel_successful", False)
        print(f"> Xoá đặt bàn thành công không: {cancel_successful}")
        next_node = END

        if cancel_successful is True:
            next_node = "successful"
        else:
            next_node = "unsuccessful"

        state["next_node"] = next_node  
        return state
            

# def booking_intent_router(state: BookingState) -> BookingState:
#     customer_want = state.get("customer_want", "")
#     print(f"> Khách muốn: {customer_want}")
#     next_node = END
    
#     if customer_want == "booking":
#         next_node = "booking"
#     elif customer_want == "modify":
#         next_node = "modify"
#     elif customer_want == "cancel":
#         next_node = "cancel"
    
#     state["next_node"] = next_node
#     return state

# def check_availble_table_router(state: BookingState) -> BookingState:
#     table_available = state.get("table_available", "")
#     print(f"> Bàn có sẵn không: {table_available}")
#     next_node = END
    
#     if table_available is True:
#         next_node = "booking_confirmation_node"
#     else:
#         next_node = "suggest_alternative_node"
    
#     state["next_node"] = next_node
#     return state
    
# def confirm_booking_router(state: BookingState) -> BookingState:
#     intent = state.get("intent", "")
#     print(f"> Khách có đồng ý hay không: {intent}")
#     next_node = END
    
#     if intent == "YES":
#         next_node = "add_customer_node"
#     elif intent == "NO":
#         next_node = "booking_node"
    
#     state["next_node"] = next_node
#     return state

# def new_customer_router(state: BookingState) -> BookingState:
#     new_customer = state.get("new_customer", "")
#     print(f"> Có phải là khách mới không: {new_customer}")
#     next_node = END
    
#     if new_customer is True:
#         next_node = "welcome_new_customer_node"
#     else:
#         next_node = "welcome_old_customer_node"
    
#     state["next_node"] = next_node
#     return state

# def check_reservation_successful_router(state: BookingState) -> BookingState:
#     reservation_successful = state.get("reservation_successful", "")
#     print(f"> Đật bàn thành công không: {reservation_successful}")
#     next_node = END
    
#     if reservation_successful is True:
#         next_node = "notify_reservation_successful_node"
#     else:
#         next_node = "apologize_customer_node"
    
#     state["next_node"] = next_node
#     return state

# def check_customer_answer_for_suggestion_router(state: BookingState) -> BookingState:
#     intent = state.get("intent", "")
#     print(f"> Khách có muốn đặt lại không: {intent}")
#     next_node = END
    
#     if intent == "yes":
#         next_node = "booking_node"
#     else:
#         next_node = "meet_again_node"
    
#     state["next_node"] = next_node
#     return state

# def exist_customer_router(state: BookingState) -> BookingState:
#     customer_id = state["booking_info"].get("customer_id", None)
#     exist_customer = True if customer_id else False
    
#     print(f"> Khách có tồn tại không: {exist_customer}")
#     next_node = END
    
#     if exist_customer is True:
#         next_node = "notify_found_customer_node"
#     else:
#         next_node = "notify_not_found_customer"
    
#     state["next_node"] = next_node
#     return state

# def exist_booking_router(state: BookingState) -> BookingState:
#     exist_reservation = state.get("exist_reservation", False)
#     customer_want = state.get("customer_want", None)
    
#     print(f"> Có tồn tại đặt bàn không: {exist_reservation}")
#     next_node = END
    
#     if customer_want == "modify":
#         if exist_reservation is True:
#             next_node = "return_customer_reservation_modify_node"
#         else:
#             next_node = "notify_not_found_booking_node"
#     elif customer_want == "cancel":
#         if exist_reservation is True:
#             next_node = "return_customer_reservation_cancel_node"
#         else:
#             next_node = "notify_not_found_booking_node"
    
#     state["next_node"] = next_node
#     return state

# def update_successful_router(state: BookingState) -> BookingState:
#     modify_successful = state.get("modify_successful", False)
#     print(f"> Cập nhật đặt bàn thành công không: {modify_successful}")
#     next_node = END
    
#     if modify_successful is True:
#         next_node = "notify_update_reservation_successful_node"
#     else:
#         next_node = "apologize_update_reservation_node"
    
#     state["next_node"] = next_node  
#     return state

# def get_confirm_cancel_router(state: BookingState) -> BookingState:
#     intent = state.get("intent", "")
#     print(f"> Khách có đồng ý huỷ bàn hay không: {intent}")
#     next_node = END
    
#     if intent == "YES":
#         next_node = "update_cancel_node"
#     elif intent == "NO":
#         next_node = "thank_you_for_not_cancel"
    
#     state["next_node"] = next_node
#     return state

# def cancel_successful_router(state: BookingState) -> BookingState:
#     cancel_successful = state.get("cancel_successful", False)
#     print(f"> Xoá đặt bàn thành công không: {cancel_successful}")
#     next_node = END
    
#     if cancel_successful is True:
#         next_node = "notify_cancel_successful_node"
#     else:
#         next_node = "notify_cancel_unsuccessful_node"
    
#     state["next_node"] = next_node  
#     return state