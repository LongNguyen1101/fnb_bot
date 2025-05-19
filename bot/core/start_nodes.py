from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from bot.core.state import BookingState
from langgraph.types import interrupt
from dotenv import load_dotenv
import os
from bot.core.graph_function import GraphFunction
from bot.chain.booking_chain import BookingChain

load_dotenv()

RESTAURANT_NAME = os.getenv("RESTAURANT_NAME")

class StartDialogue:
    def __init__(self):
        self.restaurant_name = RESTAURANT_NAME
        self.graph_function = GraphFunction()
        self.chain = BookingChain()
        
    def get_salutation(self, state: BookingState):
        customer_name = state.get("customer_name", "")
        check_salutation = state["salutation"]
        salutation = customer_name if check_salutation is None else f"{check_salutation.capitalize()}"
        return customer_name, check_salutation, salutation
        
    def announce_waiting_node(self, state: BookingState) -> BookingState:
        customer_name, check_salutation, salutation = self.get_salutation(state)
        first_sentence = f"Xin {salutation} {customer_name}" if check_salutation is not None else f"Xin {customer_name}"
        
        text = (
            f"{first_sentence} vui lòng đợi một chút để nhà hàng kiểm tra thông tin giúp quý khách ạ!"
        )
        
        # state["state"] = "ACTIVE"
        # customer = self.graph_function.add_state(state["customer_id"], state["state"])
        # if customer:
        #     print("> Thêm state ACTIVE thành công")
        # else:
        #     print("> Thêm state ACTIVE không thành công")
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
        
    def check_exists_customer_node(self, state: BookingState) -> BookingState:
        customer = self.graph_function.get_exists_customer(psid=state["customer_psid"])
        
        if customer is None:
            print(f"> Không thấy thông tin khách hàng -> tạo mới")
            new_customer = self.graph_function.add_customer(state=state)
            if new_customer is not None:
                print(f"> Thêm khách thành công")
                state["customer_id"] = new_customer.customer_id
        else:
            print(f"> Khách tồn tại")
            if customer.phone_number is None:
                print(f"> Không thấy số điện thoại khách hàng")
            else:
                print(f"> Thấy số điện thoại khách hàng")
                state["customer_phone_number"] = customer.phone_number
                
            state["customer_id"] = customer.customer_id
            
            if customer.salutation is None:
                print(f"> Không biết danh xưng của khách -> hỏi khách")
            else:
                state["salutation"] = customer.salutation
                print(f"> Biết danh xưng của khách là: {customer.salutation}")
        
        return state
    
    def ask_for_salutation_node(sefl, state: BookingState) -> BookingState:
        text = (
            "Dạ, cho phép nhà hàng được hỏi nhà hàng nên xưng hô với mình như thế nào ạ? "
            "Ví dụ như anh, chị, hoặc tên của quý khách để nhà hàng tiện xưng hô cho phù hợp hơn ạ 😊"
        )
        
        state["messages"] = add_messages(state["messages"], [AIMessage(content=text)])
        return state
    
    def get_salutation_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        customer_name = state["customer_name"]
        
        extract_data = self.chain.extract_salutaion().invoke({
            "user_input": user_input,
            "customer_name": customer_name
        })
        
        salutation = extract_data.content
        print(f"> Khách muốn đươc gọi là: {salutation}")
        
        updated_customer = self.graph_function.add_salutation(state["customer_id"], salutation)
        print(f">>> Danh xưng của khách: {updated_customer.salutation}")
        if updated_customer:
            print(f"> Thêm danh xưng thành công")
        else:
            print(f"> Lỗi thêm danh xưng")
        
        state["salutation"] = salutation
        return state
    
    def get_user_input_end_node(self, state: BookingState) -> BookingState:
        user_input = interrupt(None)
        state["intent"] = None
        state["user_input"] = user_input
        state["messages"] = add_messages(state["messages"], [HumanMessage(content=user_input)])
        return state