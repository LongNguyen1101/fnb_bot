from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel
from langchain_core.messages import AIMessage
import uuid
import json
from bot.core.graph import build_graph
from bot.core.state import init_state
from langgraph.types import Command

chatbot_router = APIRouter()
graph = build_graph()

class UserInitInput(BaseModel):
    thread_id: Optional[str] = None  # ID phiên người dùng
    message: Any  # Tin nhắn hoặc input từ người dùng
    customer_psid: Optional[str]
    customer_name: Optional[str]
    intent: Optional[str]
    
class UserContinueInput(BaseModel):
    thread_id: Optional[str] = None  # ID phiên người dùng
    message: Any  # Tin nhắn hoặc input từ người dùng

async def stream_messages(events: Any, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    seen_messages = set()  # Sử dụng set để kiểm tra tin nhắn trùng lặp nhanh hơn

    try:
        for event in events:  # Sử dụng async for để xử lý stream hiệu quả
            for node, value in event.items():
                if "messages" in value and value["messages"]:
                    message: AIMessage = value["messages"][-1]
                    message_tuple = (message.content, message.type)  # Tạo tuple để so sánh

                    # Kiểm tra tin nhắn trùng lặp
                    if message_tuple not in seen_messages:
                        seen_messages.add(message_tuple)
                        message_dict = {
                            "content": message.content,
                            "type": message.type,
                            "id": message.id,
                            "thread_id": thread_id
                        }
                        yield f"data: {json.dumps(message_dict, ensure_ascii=False)}\n\n"

    except Exception as e:
        error_dict = {"error": str(e), "thread_id": thread_id}
        yield f"data: {json.dumps(error_dict, ensure_ascii=False)}\n\n"
        
        
@chatbot_router.post("/get_introduce", summary="Get introduce in chatbot with streaming")
async def get_introduce(user_input: UserInitInput):
    try:
        state = init_state()
        state["customer_psid"] = user_input.customer_psid
        state["customer_name"] = user_input.customer_name
        state["intent"] = user_input.intent
        state["user_input"] = user_input.message
        print(f">>> Kiểm tra khách nhắn trong API: {state["user_input"]}")
        
        thread_id = user_input.thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Stream các tin nhắn từ graph
        events = graph.stream(state, config)
        return StreamingResponse(
            stream_messages(events, thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chatbot_router.post("/interact", summary="Interact with chatbot with streaming")
async def interact(user_input: UserContinueInput):
    try:
        thread_id = user_input.thread_id
        if not thread_id:
            raise HTTPException(status_code=400, detail="Thread ID is required")

        config = {"configurable": {"thread_id": thread_id}}
        human_message = Command(resume=user_input.message)

        # Stream các tin nhắn từ graph
        events = graph.stream(human_message, config)
        return StreamingResponse(
            stream_messages(events, thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))