from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from bot.core.state import BookingState
from langgraph.types import interrupt
from dotenv import load_dotenv
import os
from google import genai
from bot.core.graph_function import (
    fetch_restaurant_info,
    fetch_restaurant_branches,
    classify_user_request
)

load_dotenv()

client = genai.Client()
MODEL_NAME = os.getenv('MODEL_NAME')

# GREETING NODES
def welcome_node(state: BookingState) -> BookingState:
    if not state.get("restaurant_info"):
        state = fetch_restaurant_info(state)
    
    # prompt = (
    #     "Tạo một câu chào hỏi thân thiện và đa dạng dựa trên thông tin nhà hàng sau:\n"
    #     f"- Tên: {state['restaurant_info'].get('name', '')}\n"
    #     f"- Miêu tả nhà hàng: {state['restaurant_info'].get('description', '')}\n"
    #     "Ví dụ: Xin chào! Chào mừng bạn đến với nhà hàng [Tên].\n"
    #     "Lưu ý chỉ trả về DUY NHẤT MỘT CÂU CHÀO."
    # )
    # response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    
    restaurant_name = state['restaurant_info'].get('name', 'chúng tôi')
    description = state['restaurant_info'].get('description', '')
    
    response = (
        f"Chào mừng đến với nhà hàng {restaurant_name}.\n"
        f"{description}"
    )
    
    welcome_message = AIMessage(content=response.strip())
    
    # Cập nhật state với tin nhắn chào bằng add_messages
    state["messages"] = add_messages(state["messages"], [welcome_message])
    return state

def introduce_node(state: BookingState) -> BookingState:
    if not state.get("restaurant_branches"):
        state = fetch_restaurant_branches(state)
    
    prompt = (
        "Tạo một câu giới thiệu về thông tin nhà hàng sau:\n"
        f"- Tên: {state['restaurant_info'].get('name', '')}\n"
        f"- Thông tin chi nhánh: {state['restaurant_branches']}\n"
        "Lưu ý không được chào hỏi vì đã có câu chào hỏi trước đó.\n"
        "Nếu có nhiều chi nhánh thì hãy trả lời dưới dạng liệt kê.\n"
        f"Nếu chỉ có một chi nhánh thì hãy nói nhà hàng {state['restaurant_info'].get('name', '')}"
        "có một chi nhánh duy nhất và đưa ra các thông tin của chi nhánh đã cung cấp trước đó."
    )
    
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    
    introduce_message = AIMessage(content=response.text.strip())
    
    state["messages"] = add_messages(state["messages"], [introduce_message])
    return state

def support_node(state: BookingState) -> BookingState:
    text = f"Bạn muốn đặt bàn, thay đổi thông tin đặt bàn, huỷ đặt bàn hay nhà hàng {state['restaurant_info'].get('name', '')} có thể hỗ trợ điều gì cho bạn? 😊"
    
    support_msg = AIMessage(content=text)
    state["messages"] = add_messages(state["messages"], [support_msg])
    
    return state

def get_user_intent_node(state: BookingState):
    user_request = interrupt(None)

    customer_want = classify_user_request(user_request)
    
    state["customer_want"] = customer_want
    state["messages"] = add_messages(state["messages"], [HumanMessage(user_request)])
    state["user_input"] = user_request
    
    return state
