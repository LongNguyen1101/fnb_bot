from sqlalchemy.orm import Session

from bot.utils.database import get_db
from bot.services.crud_public import PublicCRUD
from bot.services.crud_vector_schema import VectorCRUD
from bot.schema.models import Table, Customer, Reservation
from bot.core.state import BookingState
from fastapi import Depends
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from bot.chain.booking_chain import BookingChain
from datetime import datetime, date, time as dtime, timedelta

from dotenv import load_dotenv
import os
import re
from google import genai

load_dotenv()

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
        
class GraphFunction:
    def __init__(self):
        self.chain = BookingChain()

    def check_user_phone(self, user_input: str):
        result = self.chain.check_phone_chain().invoke(user_input)
        return result.content
    
    def get_exists_customer(self, psid, public_crud: PublicCRUD = next(get_public_crud())) -> Customer:
        try:
            customer = public_crud.get_customer_by_psid(psid=psid)

            return customer
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            raise
        
    def add_customer(self, state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> Customer:
        try:
            psid = state["customer_psid"]
            name = state["customer_name"]
            customer = public_crud.create_customer(
                name=name,
                phone_number=None,
                psid=psid
            )

            return customer
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            raise
        
    def add_customer_phone_number(self, state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> Customer:
        try:
            psid = state["customer_psid"]
            phone_number = state["customer_phone_number"]
            data = {
                "phone_number": phone_number
            }
            customer = public_crud.update_customer_by_psid(psid=psid, data=data)

            return customer
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            raise
    
    def extract_phone_number(self, text):
        # Tìm chuỗi số có từ 9 đến 11 chữ số liên tục
        match = re.search(r'\b\d{9,11}\b', text)
        if match:
            return match.group()
        return None
    
    def check_missing_information(self, state: BookingState) -> List[str]:
        missing_information = []
        
        if state["date"] is None:
            missing_information.append("date")
        if state["time"] is None:
            missing_information.append("time")
        if state["people"] is None:
            missing_information.append("people")
        if state["note"] is None:
            missing_information.append("note")
        
        return missing_information
    
    def check_inappropriate_information(self, state: BookingState) -> List[str]:
        booking_date = state["date"]
        booking_time = state["time"]
        people = state["people"]
        
        inappropriate_information_note = []
        
        today = date.today()
        now = datetime.now()
        max_date = today + timedelta(days=90)  # Giới hạn 3 tháng
        open_time = dtime(10, 0)
        close_time = dtime(22, 0)
        
        if booking_date is not None:
            booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
            if booking_date < today:
                note = f"Ngày đặt đã qua. Hôm nay là {today} nhưng khách đặt ngày {booking_date}"
                inappropriate_information_note.append(note)
            
            if booking_date > max_date:
                note = "Nhà hàng chỉ nhận đặt bàn trong vòng 3 tháng tới."
                inappropriate_information_note.append(note)

            # Nếu là hôm nay, kiểm tra giờ phải sau giờ hiện tại
            if booking_date == today and booking_time <= now.time():
                note = f"Thời gian đặt đã qua. Vui lòng chọn thời gian sau {now}"
                inappropriate_information_note.append(note)
                
        if booking_time is not None:
            booking_time = datetime.strptime(booking_time, "%H:%M").time()

            # Kiểm tra giờ trong khung thời gian cho phép
            if booking_time < open_time or booking_time > close_time:
                note = "Nhà hàng chỉ nhận đặt bàn từ 10:00 đến 22:00."
                inappropriate_information_note.append(note)

        if people is not None:
            if people == 0:
                note = "Số lượng khách không phù hợp."
                inappropriate_information_note.append(note)

            if people > 50:
                note = "Nhà hàng chỉ nhận tối đa 50 khách."
                inappropriate_information_note.append(note)
            
        return inappropriate_information_note
        
    def find_available_table(self, state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Table]:
        try:
            available_table = public_crud.get_available_table(state["date"], state["time"], state["people"])
            return available_table
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            raise
        
    def add_reservation(self, state: BookingState, public_crud: PublicCRUD = next(get_public_crud())) -> Reservation:
        try:
            date = state["date"]
            time = state["time"]
            people = state["people"]
            note = state["note"]
            customer_id = state["customer_id"]
            table_id = state["table_id"]
            branch_id = 1
            policy_id = 3
            status = "confirmed"

            reservation = public_crud.create_reservation(
                table_id=table_id,
                customer_id=customer_id,
                branch_id=branch_id,
                policy_id=policy_id,
                reservation_date=date,
                reservation_time=time,
                party_size=people,
                status=status,
                note=note
            )


            add_reservation_history = public_crud.create_reservation_history(
                customer_id=customer_id,
                reservation_id=reservation.reservation_id,
                reservation_date=date,
                status="confirmed"
            )

            add_reservation_log = public_crud.create_reservation_log(
                reservation_id=reservation.reservation_id,
                action="confirmed",
                details="Tạo bàn thành công"
            )

            public_crud.db.commit()
            return reservation
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            raise
        
    def get_reservations_of_customer(self, state: BookingState, 
                                     public_crud: PublicCRUD = next(get_public_crud())) -> Optional[List[Dict[str, Any]]]:
        try:
            customer_id = state["customer_id"]
            list_reservation = public_crud.get_confirmed_reservations_by_customer(customer_id)

            data = []

            for reservation in list_reservation:
                parse_reservation_date = reservation.reservation_date.strftime('%d/%m/%Y')
                parse_reservation_time = reservation.reservation_time.strftime('%H:%M')

                data.append({
                    "table_id": reservation.table_id,
                    "reservation_id": reservation.reservation_id,
                    "reservation_date": parse_reservation_date,
                    "reservation_time": parse_reservation_time,
                    "party_size": reservation.party_size,
                    "note": reservation.note if reservation.note != "" else "Không có ghi chú"
                })

            return data
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            raise
        
    def get_capacity_in_reservation(self, state: BookingState, 
                                    public_crud: PublicCRUD = next(get_public_crud())) -> int:
        
        try:
            reservation_id = state["reservation_id_chosen"]
            capacity = public_crud.get_capacity_by_reservation_id(reservation_id=reservation_id)
            return capacity
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            raise
        
    def update_reservation_info(self, state: BookingState,
                                public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Reservation]:
        try:
            update_data = {
                "table_id": state["table_id"],
                "reservation_date": state["date"], 
                "reservation_time": state["time"],
                "party_size": state["people"],
                "note": state["note"]
            }

            updated_reservation = public_crud.update_reservation(
                reservation_id=state["reservation_id_chosen"],
                data=update_data
            )

            updated_reservation_history = public_crud.update_reservation_history_by_reservation_id(
                reservation_id=updated_reservation.reservation_id,
                data={
                    "reservation_date": state["date"]
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
        
    def get_reservation_info(self, state: BookingState,
                             public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Reservation]:
        try:
            reservation_id_chosen = state["reservation_id_chosen"]
            reservation = public_crud.get_reservation(reservation_id=reservation_id_chosen)
            public_crud.db.commit()
            return reservation
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            return None
        
    def cancel_reservation(self, state: BookingState,
                           public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Reservation]:
        try:
            update_data = {
                "status": "cancelled"
            }

            updated_reservation = public_crud.update_reservation(
                reservation_id=state["reservation_id_chosen"],
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

            public_crud.db.commit()
            return updated_reservation
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            return None
        
    def add_salutation(self, custoemr_id: int, salutation: str,
                       public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Customer]:
        
        update_data = {
            "salutation": salutation
        }
        
        try:
            updated_customer = public_crud.update_customer(custoemr_id, update_data)
            public_crud.db.commit()
            return updated_customer
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            return None
        
    def add_state(self, custoemr_id: int, state: str,
                  public_crud: PublicCRUD = next(get_public_crud())) -> Optional[Customer]:
        
        update_data = {
            "state": state
        }
        
        try:
            updated_customer = public_crud.update_customer(custoemr_id, update_data)
            public_crud.db.commit()
            return updated_customer
        except SQLAlchemyError as e:
            public_crud.db.rollback()
            return None