# BOOKINGTABLE/bot/langgraph/nodes.py
from fastapi import Depends
from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from bot.services.crud_vector_schema import VectorCRUD
from bot.schema.models import Table, Restaurant
from typing import Dict, Any
from datetime import date, time, datetime

import google as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = genai.Client()
MODEL_NAME = os.getenv('MODEL_NAME')

def get_public_crud(db: Session = Depends(get_db())):
    return PublicCRUD(db)

def get_vectror_crud(db: Session = Depends(get_db())):
    return VectorCRUD(db)

def fetch_restaurant_info(
    state: Dict[str, Any], 
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    restaurant_id = state.get('restaurant_id', 1)
    restaurant_info = public_crud.get_restaurant(restaurant_id=restaurant_id)
    
    if restaurant_info:
        # Lấy thông tin cơ bản của nhà hàng
        state["restaurant_info"] = {
            "name": restaurant_info.name,
            "description": restaurant_info.description
        }
    else:
        state["restaurant_info"] = None
    return state

def fetch_restaurant_branches(
    state: Dict[str, Any],
    public_crud: PublicCRUD = Depends(get_public_crud)
):
    restaurant_id = state.get('restaurant_id', 1) 
    branches = public_crud.get_branches_by_restaurant_id(restaurant_id=restaurant_id)
    
    if branches:
        state["restaurant_branches"] = branches
    else:
        state["restaurant_branches"] = None
    return state

def greet_customer(state: Dict[str, Any], ) -> Dict[str, Any]:
    """Chào khách hàng."""
    if not state.get("greeting_done", False):
        if state['restaurant_info'] is None:
            state['restaurant_info'] = fetch_restaurant_info(state)
            
        prompt = (
            "Tạo một câu chào hỏi thân thiện và đa dạng dựa trên thông tin nhà hàng sau:\n"
            f"- Tên: {state['restaurant_info']}\n"
            "Ví dụ: Xin chào! Chào mừng bạn đến với nhà hàng [Tên]."
        )
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        state["messages"].append({"role": "assistant", "content": response.text})
        state["greeting_done"] = True
    return state

def introduce_restaurant(state: Dict[str, Any]) -> Dict[str, Any]:
    if not state.get("intro_done", False):
        if state['restaurant_branches'] is None:
            state['restaurant_branches'] = fetch_restaurant_branches(state)
        
        prompt = (
            "Tạo một câu giới thiệu về thông tin nhà hàng sau:\n"
            f"- Tên: {state['restaurant_info']['name']}\n"
            f"- Thông tin chi nhánh: {state['restaurant_branches']}\n"
        )
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        state["messages"].append({"role": "assistant", "content": response.text})
        state["intro_done"] = True
    return state

def find_table(state: Dict[str, Any], public_crud: PublicCRUD = next(get_public_crud())) -> Dict[str, Any]:
    user_input = state.get("user_input", "")

    if not state.get("table_id"):
        prompt = (
            "Phân tích câu sau và trích xuất các thông tin sau:\n"
            "- Ngày đặt bàn (định dạng: dd/mm/yyyy)\n"
            "- Giờ đặt bàn (định dạng: HH:MM)\n"
            "- Số người\n"
            "Nếu không tìm thấy thông tin nào, trả về giá trị null.\n"
            f"Câu: \"{user_input}\"\n"
            "Trả về dưới dạng JSON:\n"
            "{\n"
            "    \"reservation_date\": \"dd/mm/yyyy\" hoặc null,\n"
            "    \"reservation_time\": \"HH:MM\" hoặc null,\n"
            "    \"party_size\": số hoặc null\n"
            "}"
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        try:
            extracted_info = json.loads(response.text.strip())
            reservation_date = extracted_info["reservation_date"]
            reservation_time = extracted_info["reservation_time"]
            party_size = extracted_info["party_size"]

            if reservation_date and reservation_time and party_size:
                reservation_date = datetime.strptime(reservation_date, "%d/%m/%Y").date()
                reservation_time = datetime.strptime(reservation_time, "%H:%M").time()
                party_size = int(party_size)

                branch_id = state.get("branch_id", 1)
                available_tables = public_crud.db.query(Table).filter(
                    Table.branch_id == branch_id,
                    Table.capacity >= party_size,
                    Table.is_active == True
                ).all()

                if available_tables:
                    table = available_tables[0]  # Chọn bàn đầu tiên
                    state["table_id"] = table.table_id
                    state["reservation_date"] = reservation_date
                    state["reservation_time"] = reservation_time
                    state["party_size"] = party_size
                    response = f"Tôi đã tìm thấy bàn {table.table_number} cho {party_size} người vào ngày {reservation_date} lúc {reservation_time}. Vui lòng cung cấp thông tin của bạn."
                else:
                    response = "Rất tiếc, không có bàn nào phù hợp với yêu cầu của bạn. Bạn có muốn thử thời gian khác không?"
            else:
                response = "Vui lòng cung cấp ngày, giờ và số người (ví dụ: 'ngày 15/04/2025 18:00 cho 4 người')."
        except Exception as e:
            response = "Tôi không hiểu yêu cầu của bạn. Vui lòng cung cấp ngày, giờ và số người (ví dụ: 'ngày 15/04/2025 18:00 cho 4 người')."

        state["messages"].append({"role": "assistant", "content": response})
    return state

def collect_customer_info(state: Dict[str, Any], public_crud: PublicCRUD = next(get_public_crud())) -> Dict[str, Any]:
    user_input = state.get("user_input", "")

    if state.get("table_id") and not state.get("customer_id"):
        prompt = (
            "Phân tích câu sau và trích xuất các thông tin sau:\n"
            "- Tên khách hàng\n"
            "- Số điện thoại\n"
            "- Email (nếu có)\n"
            "Nếu không tìm thấy thông tin nào, trả về giá trị null.\n"
            f"Câu: \"{user_input}\"\n"
            "Trả về dưới dạng JSON:\n"
            "{\n"
            "    \"name\": \"tên\" hoặc null,\n"
            "    \"phone\": \"số điện thoại\" hoặc null,\n"
            "    \"email\": \"email\" hoặc null\n"
            "}"
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        try:
            extracted_info = json.loads(response.text.strip())
            name = extracted_info["name"]
            phone = extracted_info["phone"]
            email = extracted_info["email"]

            if name and phone:
                customer = public_crud.create_customer(name=name, phone_number=phone, email=email)
                state["customer_id"] = customer.customer_id
                state["customer_name"] = name
                state["customer_phone"] = phone
                state["customer_email"] = email
                response = f"Thông tin của bạn đã được lưu: {name}, {phone}. Bạn có muốn xác nhận đặt bàn không?"
            else:
                response = "Vui lòng cung cấp tên và số điện thoại của bạn (ví dụ: 'tên Nguyễn Văn A, số điện thoại +84912345678, email abc@example.com')."
        except Exception as e:
            response = "Tôi không hiểu thông tin bạn cung cấp. Vui lòng cung cấp tên và số điện thoại (ví dụ: 'tên Nguyễn Văn A, số điện thoại +84912345678')."

        state["messages"].append({"role": "assistant", "content": response})
    return state

def confirm_booking(state: Dict[str, Any], public_crud: PublicCRUD = next(get_public_crud())) -> Dict[str, Any]:
    user_input = state.get("user_input", "").lower()
    
    if state.get("customer_id") and state.get("table_id") and not state.get("booking_confirmed", False):
        prompt = (
            "Xác định ý định của câu sau:\n"
            "- Nếu người dùng muốn xác nhận (ví dụ: 'xác nhận', 'có', 'ok'), trả về \"confirm\".\n"
            "- Nếu không, trả về \"not_confirm\".\n"
            f"Câu: \"{user_input}\""
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        intent = response.text.strip()

        if intent == "confirm":
            reservation = public_crud.create_reservation(
                table_id=state["table_id"],
                customer_id=state["customer_id"],
                branch_id=state["branch_id"],
                policy_id=1,  
                reservation_date=state["reservation_date"],
                reservation_time=state["reservation_time"],
                party_size=state["party_size"],
                status="confirmed"
            )
            state["booking_confirmed"] = True
            response = f"Đặt bàn của bạn đã được xác nhận! Mã đặt bàn: {reservation.reservation_id}. Cảm ơn bạn!"
        else:
            response = "Bạn có muốn xác nhận đặt bàn không? (nói 'xác nhận' hoặc 'có' để tiếp tục)"

        state["messages"].append({"role": "assistant", "content": response})
    return state