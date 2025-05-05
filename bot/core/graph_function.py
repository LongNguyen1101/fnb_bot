from sqlalchemy.orm import Session
from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from bot.services.crud_vector_schema import VectorCRUD
from bot.schema.models import Table, Customer, Reservation
from bot.core.state import BookingState
from fastapi import Depends
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError

from dotenv import load_dotenv
import os
import re
from google import genai

load_dotenv()

client = genai.Client()
MODEL_NAME = os.getenv('MODEL_NAME')

def get_public_crud():
    """Generator function to provide a PublicCRUD instance with a database session."""
    db: Session = next(get_db())
    try:
        yield PublicCRUD(db)
    finally:
        db.close()

def get_vector_crud():
    """Generator function to provide a VectorCRUD instance with a database session."""
    db: Session = next(get_db())
    try:
        yield VectorCRUD(db)
    finally:
        db.close()

def fetch_restaurant_info(state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> BookingState:
    try:
        restaurant_id = state.get('restaurant_id', 1)
        restaurant_info = public_crud.get_restaurant(restaurant_id=restaurant_id)
        
        if restaurant_info:
            state["restaurant_info"] = {
                "name": restaurant_info.name,
                "description": restaurant_info.description
            }
        else:
            state["restaurant_info"] = {}
        return state
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def fetch_restaurant_branches(state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> BookingState:
    try:
        restaurant_id = state.get('restaurant_id', 1)
        branches = public_crud.get_branches_by_restaurant_id(restaurant_id=restaurant_id)
        
        if branches:
            state["restaurant_branches"] = [{
                'branch_id': branch.branch_id,
                'address': branch.address,
                'opening_time': branch.opening_time,
                'closing_time': branch.closing_time,
                'max_capacity': branch.max_capacity
            } for branch in branches]
        else:
            state["restaurant_branches"] = []
        return state
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def classify_user_request(user_input) -> str:
    prompt = (
        "Dựa vào câu yêu cầu của khách hàng để xác định câu yêu cầu này thuộc loại nào: \n"
        "- 'booking': nếu yêu cầu của khách có ý định đặt bàn\n"
        "- 'modify': nếu yêu cầu của khách có ý định thay đổi thông tin đặt bàn\n"
        "- 'cancel': nếu yêu cầu của khách có ý định huỷ đặt bàn\n"
        "### Ví dụ: \n"
        "Input: Tôi muốn đặt bàn cho bữa tối.\n"
        "Output: booking\n"
        "Input: Tôi muốn thay đổi thông tin đặt bàn của tôi.\n"
        "Output: modify\n"
        "Input: Tôi muốn huỷ thông tin đặt bàn của tôi.\n"
        "Output: cancel\n"
        f"Yêu cầu của khách {user_input}\n"
        "Lưu ý chỉ cho ra output là một trong ba giá trị: booking, modify, cancel.\n"
        "KHÔNG IN RA THÊM CÁC CHỮ KHÁC NGOÀI BA CHỮ ĐÃ LIỆT KÊ"
    )
    
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip().lower()

def fetch_available_tables(state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> List[Table]:
    try:
        available_tables = public_crud.get_available_tables(state["booking_info"]["branch_id"])
        return available_tables
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def find_available_table(state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> Table:
    try:
        party_size = state["booking_info"]["party_size"]
        available_tables = fetch_available_tables(state, public_crud)
        capacities = [table.capacity for table in available_tables]
        print(capacities)
        table_found = None
        
        for table in available_tables:
            if table.capacity == party_size:
                table_found = table
                break
            elif table.capacity > party_size and table.capacity - party_size <= 3:
                table_found = table
                break
        
        return table_found
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def check_exist_customer_by_phone_number(state: BookingState, 
                                         public_crud: PublicCRUD = next(get_public_crud())) -> Customer:
    try:
        phone_number = state["booking_info"].get("phone_number", None)
        if phone_number is None:
            raise ValueError("Not found phone number of customer!!")
        
        exist_customer = public_crud.get_customer_by_phone_number(phone_number=phone_number)
        return exist_customer
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def add_customer(state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> Customer:
    try:
        customer = public_crud.create_customer(
            name=state["booking_info"]["full_name"],
            phone_number=state["booking_info"]["phone_number"],
            email=state["booking_info"].get("email", "")
        )
        public_crud.db.commit()
        return customer
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def get_welcome_new_customer_text(state: BookingState) -> str:
    prompt = (
        "Bạn là một chuyên gia trong việc giao tiếp với khách hàng.\n"
        "Hãy viết một câu chào hỏi khách hàng mới với tông giọng lịch sự cho hệ thống chatbot đặt bàn của chúng tôi "
        "với các thông tin được cung cấp dưới đây:\n"
        f"- Tên nhà hàng: {state["restaurant_info"].get("name", "chúng tôi")}\n"
        f"- Tên khách hàng: {state["booking_info"].get("full_name", "quý khách")}\n"
        "### Ví dụ:\n"
        "Chào mừng [Tên khách hàng] đến với nhà hàng [Tên nhà hàng]. Nhà hàng [Tên nhà hàng] "
        "vừa tạo tài khoản mới cho quý khách dựa vào các thông tin được cung cấp.\n"
        "Quý khách hãy sử dụng số điện thoại này để thay đổi thông tin hoặc huỷ đặt bàn.\n"
        "Nếu quý khách có thắc mắc liên quan đến thông tin đặt bàn, hãy liên hệ với nhà hàng [Tên nhà hàng] "
        "và sử dụng số điện thoại này để chúng tôi giải đáp thắc mắc của quý khách một cách nhanh nhất.\n"
        "### LƯU Ý:\n"
        "Ở trên chỉ là ví dụ của câu bạn cần tạo ra, hãy tạo ra DUY NHẤT MỘT CÂU tương tự với câu trên.\n"
        "Trong câu bạn tạo ra luôn luôn phải đầy đủ thông tin sau đây:\n"
        "- Tên nhà hàng.\n"
        "- Tên khách hàng.\n"
        "- Phải có câu liên quan đến việc thay đổi hay huỷ đặt bàn.\n"
        "- Phải có câu liên quan đến việc giải đáp thắc mắc."
    )
    
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip()

def add_reservation(state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> Reservation:
    try:
        table_id = state["booking_info"]["table_id"]
        customer_id = state["customer_id"]
        branch_id = state["booking_info"]["branch_id"]
        policy_id = 3  # Cancellation Fee policy
        reservation_date = state["booking_info"]["reservation_date"]
        reservation_time = state["booking_info"]["reservation_time"]
        party_size = state["booking_info"]["party_size"]
        status = "confirmed"
        
        reservation = public_crud.create_reservation(
            table_id=table_id,
            customer_id=customer_id,
            branch_id=branch_id,
            policy_id=policy_id,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            party_size=party_size,
            status=status
        )
        
        table_status_update = public_crud.update_table_status_by_table_id(
            table_id=table_id,
            data={"status": "reserved"}
        )
        
        add_reservation_history = public_crud.create_reservation_history(
            customer_id=customer_id,
            reservation_id=reservation.reservation_id,
            reservation_date=reservation_date,
            status="confirmed"
        )
        
        add_reservation_log = public_crud.create_reservation_log(
            reservation_id=reservation.reservation_id,
            action="confirmed",
            details=""
        )
        
        public_crud.db.commit()
        return reservation
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def get_notify_reservation_successful(state: BookingState, 
                                      public_crud: PublicCRUD = next(get_public_crud())) -> str:
    try:
        restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
        customer_name = state["booking_info"].get("full_name", "quý khách")
        reservation_time = state["booking_info"].get("reservation_time", "Thời gian quý khách đã đặt.")
        policy_id = 3
        policy_details = public_crud.get_policy_details_by_policy_id(policy_id=policy_id)
        print(policy_details)
        
        prompt = (
            "Bạn là nhân viên phục vụ nhà hàng có nhiều năm kinh nghiệm và phong cách nói chuyện lịch sự và trang trọng.\n"
            "Bạn hãy chúc mừng khách hàng đã đặt bàn thành công với các thông tin được cung cấp sau đây:\n"
            f"- Tên nhà hàng: {restaurant_name}.\n"
            f"- Tên khách hàng: {customer_name}.\n"
            f"- Thông tin về chính sách huỷ đặt bàn: {policy_details}.\n"
            f"- Thời gian đặt bàn: {reservation_time}\n"
            "Hãy tạo ra MỘT câu chúc mừng khách đã đặt bàn thành công.\n"
            "### LƯU Ý:\n"
            "- Luôn viết hoa chữ cái đầu tiên của tên khách hàng.\n"
            "- Dựa vào thông tin về chính sách huỷ bàn và viết lại một cách dễ hiểu cho khách hàng."
        )
        
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        return response.text.strip()
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def classify_intent_for_suggestion(user_input) -> str:
    prompt = (
        "Bạn là nhân viên phục vụ nhà hàng có nhiều năm kinh nghiệm và phong cách nói chuyện lịch sự và trang trọng.\n"
        "Dựa vào câu yêu cầu của khách hàng để xác định câu yêu cầu này thuộc loại WHICH: \n"
        "- 'no': nếu khách hàng không muốn thay đổi giờ đặt bàn.\n"
        "- 'yes': nếu khách hàng có ý định muốn thay đổi thông tin đặt bàn.\n"
        "### Ví dụ: \n"
        "Input: Tôi không muốn thay đổi giờ đặt bàn.\n"
        "Output: no\n"
        "Input: Tôi chỉ rảnh vào lúc này.\n"
        "Output: no\n"
        "Input: Tôi muốn thử một giờ đặt bàn khác.\n"
        "Output: yes\n"
        f"Yêu cầu của khách {user_input}\n"
    )
    
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip().lower()

def get_meet_again_text(state: BookingState) -> str:
    restaurant_name = state["restaurant_info"].get("name", "chúng tôi")
    customer_name = state["booking_info"].get("full_name", "quý khách")
    
    prompt = (
        "Bạn là nhân viên phục vụ nhà hàng có nhiều năm kinh nghiệm và phong cách nói chuyện lịch sự và trang trọng.\n"
        "Dựa vào thông tin dưới đây: \n"
        f"- Tên nhà hàng: {restaurant_name}.\n"
        f"- Tên khách hàng: {customer_name}.\n"
        "Hãy viết một câu để hẹn gặp lại khách."
    )
    
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text.strip()

def extract_phone_number(text):
    # Tìm chuỗi số có từ 9 đến 11 chữ số liên tục
    match = re.search(r'\b\d{9,11}\b', text)
    if match:
        return match.group()
    return None

def get_reservations_of_customer(state: BookingState, 
                                 public_crud: PublicCRUD = next(get_public_crud())) -> Optional[List[Dict[str, Any]]]:
    try:
        customer_id = state["booking_info"]["customer_id"]
        list_reservation = public_crud.get_confirmed_reservations_by_customer(customer_id)
        list_branch_id = [reservation.branch_id for reservation in list_reservation]
        list_branch_addresses = [public_crud.get_restaurant_branches(branch_id) for branch_id in list_branch_id]
        
        data = []
        
        for reservation, branch in zip(list_reservation, list_branch_addresses):
            parse_reservation_date = reservation.reservation_date.strftime('%d/%m/%Y')
            parse_reservation_time = reservation.reservation_time.strftime('%H:%M')
            
            data.append({
                "reservation_id": reservation.reservation_id,
                "branch_id": reservation.branch_id,
                "address": branch.address,
                "reservation_date": parse_reservation_date,
                "reservation_time": parse_reservation_time,
                "party_size": reservation.party_size
            })
        
        return data
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        raise

def update_reservation_info(state: BookingState,
                            public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Reservation]:
    try:
        update_data = {
            "branch_id": state["booking_info"]["branch_id"],
            "reservation_date": state["booking_info"]["reservation_date"], 
            "reservation_time": state["booking_info"]["reservation_time"],
            "party_size": state["booking_info"]["party_size"],
        }

        updated_reservation = public_crud.update_reservation(
            reservation_id=state["booking_info"]["reservation_id_chosen"],
            data=update_data
        )

        updated_reservation_history = public_crud.update_reservation_history_by_reservation_id(
            reservation_id=updated_reservation.reservation_id,
            data={
                "reservation_date": state["booking_info"]["reservation_date"]
            }
        )

        add_modify_reservation_log = public_crud.create_reservation_log(
            reservation_id=updated_reservation.reservation_id,
            action="modified",
            details="Khách hàng sửa lại thông tin đặt bàn"
        )
        
        public_crud.db.commit()
        return updated_reservation
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        return None

def cancel_reservation(state: BookingState,
                       public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Reservation]:
    try:
        update_data = {
            "status": "cancelled"
        }
        
        updated_reservation = public_crud.update_reservation(
            reservation_id=state["booking_info"]["reservation_id_chosen"],
            data=update_data
        )
        
        updated_reservation_history = public_crud.update_reservation_history_by_reservation_id(
            reservation_id=updated_reservation.reservation_id,
            data=update_data
        )
        
        add_reservation_log = public_crud.create_reservation_log(
            reservation_id=updated_reservation.reservation_id,
            action="cancelled",
            details="Khách huỷ đặt bàn"
        )
        
        updated_table_status = public_crud.update_table_status_by_table_id(
            table_id=updated_reservation.table_id,
            data={"status": "available"}
        )
        
        public_crud.db.commit()
        return updated_reservation
    except SQLAlchemyError as e:
        public_crud.db.rollback()
        return None