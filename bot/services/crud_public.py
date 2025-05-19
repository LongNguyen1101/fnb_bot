# BOOKINGTABLE/bot/services/crud.py
from sqlalchemy.orm import Session
from bot.schema.models import (Restaurant, RestaurantBranch, ServiceType, Table, TableStatus, 
                             Reservation, ReservationLog, Customer, ReservationHistory, 
                             Payment, WaitingList, NoShowLog, PolicyType, Policy, PolicyDetail)
from typing import Optional, Dict, Any, List
from sqlalchemy import desc, asc, select
from datetime import datetime, timedelta, time as dt_time

# CRUD cho schema public
class PublicCRUD:
    def __init__(self, db: Session):
        self.db = db

    # Restaurant CRUD
    def create_restaurant(self, name: str, description) -> Restaurant:
        restaurant = Restaurant(
            name=name, 
            description=description
        )
        self.db.add(restaurant)
        self.db.commit()
        self.db.refresh(restaurant)
        return restaurant

    def get_restaurant(self, restaurant_id: int) -> Optional[Restaurant]:
        return self.db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()

    def update_restaurant(self, restaurant_id: int, data: Dict[str, Any]) -> Optional[Restaurant]:
        restaurant = self.get_restaurant(restaurant_id)
        if restaurant:
            for key, value in data.items():
                setattr(restaurant, key, value)
            self.db.commit()
            self.db.refresh(restaurant)
        return restaurant

    def delete_restaurant(self, restaurant_id: int) -> bool:
        restaurant = self.get_restaurant(restaurant_id)
        if restaurant:
            self.db.delete(restaurant)
            self.db.commit()
            return True
        return False
    
    # Restaurant branches CRUD
    def create_restaurant_branches(self, restaurant_id: int, address: str, opening_time: str, 
                                   closing_time: str, max_capacity: int) -> RestaurantBranch:
        restaurant_branches = RestaurantBranch(
            restaurant_id=restaurant_id,
            address=address,
            opening_time=opening_time,
            closing_time=closing_time,
            max_capacity=max_capacity
        )
        self.db.add(restaurant_branches)
        self.db.commit()
        self.db.refresh(restaurant_branches)
        return restaurant_branches

    def get_restaurant_branches(self, branch_id: int) -> Optional[RestaurantBranch]:
        return self.db.query(RestaurantBranch).filter(RestaurantBranch.branch_id == branch_id).first()
    
    def get_branches_by_restaurant_id(self, restaurant_id: int) -> Optional[RestaurantBranch]:
        return self.db.query(RestaurantBranch).filter(RestaurantBranch.restaurant_id == restaurant_id).all()
    
    def get_branches_by_ids(self, branch_ids: List[int]) -> List[RestaurantBranch]:
        return (
            self.db.query(RestaurantBranch)
            .filter(RestaurantBranch.branch_id.in_(branch_ids))
            .all()
        )

    def update_restaurant_branches(self, branch_id: int, data: Dict[str, Any]) -> Optional[RestaurantBranch]:
        restaurant_branches = self.get_restaurant_branches(branch_id)
        if restaurant_branches:
            for key, value in data.items():
                setattr(restaurant_branches, key, value)
            self.db.commit()
            self.db.refresh(restaurant_branches)
        return restaurant_branches

    def delete_restaurant_branches(self, branch_id: int) -> bool:
        restaurant_branches = self.get_restaurant_branches(branch_id)
        if restaurant_branches:
            self.db.delete(restaurant_branches)
            self.db.commit()
            return True
        return False
    
    # Service type CRUD
    def create_service_type(self, branch_id: int, service_name: str, description: str, is_active: bool) -> ServiceType:
        service_type = ServiceType(
            branch_id=branch_id,
            service_name=service_name,
            description=description,
            is_active=is_active
        )
        self.db.add(service_type)
        self.db.commit()
        self.db.refresh(service_type)
        return service_type

    def get_service_type(self, service_id: int) -> Optional[ServiceType]:
        return self.db.query(ServiceType).filter(ServiceType.service_id == service_id).first()

    def update_service_type(self, service_id: int, data: Dict[str, Any]) -> Optional[ServiceType]:
        service_type = self.get_service_type(service_id)
        if service_type:
            for key, value in data.items():
                setattr(service_type, key, value)
            self.db.commit()
            self.db.refresh(service_type)
        return service_type

    def delete_service_type(self, service_id: int) -> bool:
        service_type = self.get_service_type(service_id)
        if service_type:
            self.db.delete(service_type)
            self.db.commit()
            return True
        return False

    # Table CRUD
    def create_table(self, branch_id: int, table_number: str, capacity: int, is_active: bool = True) -> Table:
        table = Table(
            branch_id=branch_id, 
            table_number=table_number, 
            capacity=capacity, 
            is_active=is_active
        )
        self.db.add(table)
        self.db.commit()
        self.db.refresh(table)
        return table
    
    def get_capacity_by_reservation_id(self, reservation_id: int) -> int:
        result = (
            self.db.query(Table.capacity)
            .join(Reservation, Table.table_id == Reservation.table_id)
            .filter(Reservation.reservation_id == reservation_id)
            .first()
        )
        return result if result else None

    def get_table(self, table_id: int) -> Optional[Table]:
        return self.db.query(Table).filter(Table.table_id == table_id).first()

    def update_table(self, table_id: int, data: Dict[str, Any]) -> Optional[Table]:
        table = self.get_table(table_id)
        if table:
            for key, value in data.items():
                setattr(table, key, value)
            self.db.commit()
            self.db.refresh(table)
        return table

    def delete_table(self, table_id: int) -> bool:
        table = self.get_table(table_id)
        if table:
            self.db.delete(table)
            self.db.commit()
            return True
        return False
    
    def get_available_tables(self, branch_id: int) -> Optional[List[Table]]:
        return (
            self.db.query(Table)
            .join(TableStatus, Table.table_id == TableStatus.table_id)
            .filter(TableStatus.status == "available")
            .filter(Table.branch_id == branch_id)
            .order_by(asc(Table.capacity))
            .all()
        )
    
    # Table status CRUD
    def create_table_status(self, table_id: int, status: str) -> Table:
        table_stauts = TableStatus(
            table_id=table_id,
            status=status              
        )
        self.db.add(table_stauts)
        self.db.commit()
        self.db.refresh(table_stauts)
        return table_stauts

    def get_table_status(self, status_id: int) -> Optional[TableStatus]:
        return self.db.query(TableStatus).filter(TableStatus.status_id == status_id).first()
    
    def get_table_status_by_table_id(self, table_id: int) -> Optional[TableStatus]:
        return self.db.query(TableStatus).filter(TableStatus.table_id == table_id).first()

    def update_table_status(self, status_id: int, data: Dict[str, Any]) -> Optional[TableStatus]:
        table_status = self.get_table_status(status_id)
        if table_status:
            for key, value in data.items():
                setattr(table_status, key, value)
            self.db.commit()
            self.db.refresh(table_status)
        return table_status
    
    def update_table_status_by_table_id(self, table_id: int, data: Dict[str, Any]) -> Optional[TableStatus]:
        table_status = self.get_table_status_by_table_id(table_id)
        if table_status:
            for key, value in data.items():
                setattr(table_status, key, value)
            self.db.commit()
            self.db.refresh(table_status)
        return table_status

    def delete_table_status(self, status_id: int) -> bool:
        table_status = self.get_table_status(status_id)
        if table_status:
            self.db.delete(table_status)
            self.db.commit()
            return True
        return False

    # Reservation CRUD
    def create_reservation(self, table_id: int, customer_id: int, branch_id: int, policy_id: int,
                         reservation_date: str, reservation_time: str, party_size: int, 
                         status: str = "pending", note: str = "") -> Reservation:
        reservation = Reservation(
            table_id=table_id,
            customer_id=customer_id,
            branch_id=branch_id,
            policy_id=policy_id,
            reservation_date=reservation_date, 
            reservation_time=reservation_time,
            party_size=party_size, 
            status=status,
            note=note
        )
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def get_available_table(self, date: str, time: str, people: int) -> Optional[Table]:
        reservation_date = datetime.strptime(date, "%Y-%m-%d").date()
        reservation_time = datetime.strptime(time, "%H:%M").time()
        min_capacity = people
        max_capacity = people + 3 # Chỉ cho phép bàn dư 3 chỗ ngồi
        
        dt_full = datetime.combine(reservation_date, reservation_time)
        time_before = (dt_full - timedelta(hours=1)).time()
        time_after = (dt_full + timedelta(hours=1)).time()
        
        subquery_reserved_table_ids = (
            select(Reservation.table_id)
            .where(
                Reservation.reservation_date == reservation_date,
                Reservation.reservation_time.between(time_before, time_after),
                Reservation.status.in_(["pending", "confirmed"])
            )
        )

        available_tables = (
            self.db.query(Table)
            .filter(
                Table.capacity.between(min_capacity, max_capacity),
                ~Table.table_id.in_(subquery_reserved_table_ids)
            )
            .order_by(Table.capacity.asc())
            .first()
        )

        return available_tables
        
    
    def get_reservation(self, reservation_id: int) -> Optional[Reservation]:
        return self.db.query(Reservation).filter(Reservation.reservation_id == reservation_id).first()
    
    def get_reservation_by_customer_id(self, customer_id: int) -> Optional[List[Reservation]]:
        return self.db.query(Reservation).filter(Reservation.customer_id == customer_id).all()
    
    def get_confirmed_reservations_by_customer(self, customer_id: int) -> Optional[List[Reservation]]:
        return (
            self.db.query(Reservation)
            .join(ReservationHistory, Reservation.reservation_id == ReservationHistory.reservation_id)
            .filter(
                ReservationHistory.status == "confirmed",
                Reservation.customer_id == customer_id
            )
            .order_by(Reservation.reservation_date.desc(), Reservation.reservation_time.desc())
            .all()
        )

    def update_reservation(self, reservation_id: int, data: Dict[str, Any]) -> Optional[Reservation]:
        reservation = self.get_reservation(reservation_id)
        if reservation:
            for key, value in data.items():
                setattr(reservation, key, value)
            self.db.commit()
            self.db.refresh(reservation)
        return reservation

    def delete_reservation(self, reservation_id: int) -> bool:
        reservation = self.get_reservation(reservation_id)
        if reservation:
            self.db.delete(reservation)
            self.db.commit()
            return True
        return False
    
    # Reservation Log CRUD
    def create_reservation_log(self, reservation_id: int, action: str, details: str) -> ReservationLog:
        reservation_log = ReservationLog(
            reservation_id=reservation_id,
            action=action,
            details=details
        )
        self.db.add(reservation_log)
        self.db.commit()
        self.db.refresh(reservation_log)
        return reservation_log

    def get_reservation_log(self, log_id: int) -> Optional[ReservationLog]:
        return self.db.query(Reservation).filter(ReservationLog.log_id == log_id).first()
    
    def get_reservation_log_by_reservation_id(self, reservation_id: int) -> Optional[ReservationLog]:
        return self.db.query(ReservationLog).filter(ReservationLog.reservation_id == reservation_id).first()

    def update_reservation_log(self, log_id: int, data: Dict[str, Any]) -> Optional[ReservationLog]:
        reservation_log = self.get_reservation_log(log_id)
        if reservation_log:
            for key, value in data.items():
                setattr(reservation_log, key, value)
            self.db.commit()
            self.db.refresh(reservation_log)
        return reservation_log
    
    def update_reservation_log_by_reservation_id(self, reservation_id: int, 
                                                 data: Dict[str, Any]) -> Optional[ReservationLog]:
        reservation_log = self.get_reservation_log_by_reservation_id(reservation_id)
        if reservation_log:
            for key, value in data.items():
                setattr(reservation_log, key, value)
            self.db.commit()
            self.db.refresh(reservation_log)
        return reservation_log

    def delete_reservation_log(self, log_id: int) -> bool:
        reservation_log = self.get_reservation_log(log_id)
        if reservation_log:
            self.db.delete(reservation_log)
            self.db.commit()
            return True
        return False
    
    # Customer CRUD
    def create_customer(self, name: str, phone_number: str, psid: str) -> Customer:
        customer = Customer(
            name=name,
            phone_number=phone_number,
            psid=psid
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def get_customer_by_psid(self, psid: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.psid == psid).first()
    
    def get_customer_by_phone_number(self, phone_number: str) -> Optional[Customer]:
        return self.db.query(Customer).filter(Customer.phone_number == phone_number).first()

    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Optional[Customer]:
        customer = self.get_customer(customer_id)
        if customer:
            for key, value in data.items():
                setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
        return customer
    
    def update_customer_by_psid(self, psid: str, data: Dict[str, Any]) -> Optional[Customer]:
        customer = self.get_customer_by_psid(psid=psid)
        if customer:
            for key, value in data.items():
                setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
        return customer

    def delete_customer(self, customer_id: int) -> bool:
        customer = self.get_customer(customer_id)
        if customer:
            self.db.delete(customer)
            self.db.commit()
            return True
        return False
    
    # Reservation history CRUD
    def create_reservation_history(self, customer_id: int, reservation_id: int, 
                        reservation_date: str, status: str) -> ReservationHistory:
        reservation_history = ReservationHistory(
            customer_id=customer_id,
            reservation_id=reservation_id,
            reservation_date=reservation_date,
            status=status
        )
        self.db.add(reservation_history)
        self.db.commit()
        self.db.refresh(reservation_history)
        return reservation_history

    def get_reservation_history(self, history_id: int) -> Optional[ReservationHistory]:
        return self.db.query(ReservationHistory).filter(ReservationHistory.history_id == history_id).first()
    
    def get_reservation_history_by_reservation_id(self, reservation_id: int) -> Optional[ReservationHistory]:
        return self.db.query(ReservationHistory).filter(ReservationHistory.reservation_id == reservation_id).first()

    def update_reservation_history(self, history_id: int, data: Dict[str, Any]) -> Optional[ReservationHistory]:
        reservation_history = self.get_reservation_history(history_id)
        if reservation_history:
            for key, value in data.items():
                setattr(reservation_history, key, value)
            self.db.commit()
            self.db.refresh(reservation_history)
        return reservation_history
    
    def update_reservation_history_by_reservation_id(self, reservation_id: int, 
                                                     data: Dict[str, Any]) -> Optional[ReservationHistory]:
        reservation_history = self.get_reservation_history_by_reservation_id(reservation_id)
        if reservation_history:
            for key, value in data.items():
                setattr(reservation_history, key, value)
            self.db.commit()
            self.db.refresh(reservation_history)
        return reservation_history

    def delete_eservation_history(self, history_id: int) -> bool:
        reservation_history = self.get_reservation_history(history_id)
        if reservation_history:
            self.db.delete(reservation_history)
            self.db.commit()
            return True
        return False
    
    # Payment CRUD
    def create_payment(self, reservation_id: int, amount: int, 
                       payment_method: str, payment_status: str) -> Payment:
        payment = Payment(
            reservation_id=reservation_id,
            amount=amount,
            payment_method=payment_method,
            payment_status=payment_status
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, payment_id: int) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.payment_id == payment_id).first()

    def update_payment(self, payment_id: int, data: Dict[str, Any]) -> Optional[Payment]:
        payment = self.get_payment(payment_id)
        if payment:
            for key, value in data.items():
                setattr(payment, key, value)
            self.db.commit()
            self.db.refresh(payment)
        return payment

    def delete_payment(self, payment_id: int) -> bool:
        payment = self.get_payment(payment_id)
        if payment:
            self.db.delete(payment)
            self.db.commit()
            return True
        return False
    
    # Waiting list CRUD
    def create_waiting_list(self, customer_id: int, branch_id: int, requested_date: str, 
                            requested_time: str, party_size: int, status: str) -> WaitingList:
        waiting_list = WaitingList(
            customer_id=customer_id,
            branch_id=branch_id,
            requested_date=requested_date,
            requested_time=requested_time,
            party_size=party_size,
            status=status
        )
        self.db.add(waiting_list)
        self.db.commit()
        self.db.refresh(waiting_list)
        return waiting_list

    def get_waiting_list(self, wait_id: int) -> Optional[WaitingList]:
        return self.db.query(WaitingList).filter(WaitingList.wait_id == wait_id).first()

    def update_waiting_list(self, wait_id: int, data: Dict[str, Any]) -> Optional[WaitingList]:
        waiting_list = self.get_waiting_list(wait_id)
        if waiting_list:
            for key, value in data.items():
                setattr(waiting_list, key, value)
            self.db.commit()
            self.db.refresh(waiting_list)
        return waiting_list

    def delete_waiting_list(self, wait_id: int) -> bool:
        waiting_list = self.get_waiting_list(wait_id)
        if waiting_list:
            self.db.delete(waiting_list)
            self.db.commit()
            return True
        return False
    
    # No show CRUD
    def create_no_show_log(self, reservation_id: int, customer_id: int, no_show_date: str) -> NoShowLog:
        no_show_log = NoShowLog(
            reservation_id=reservation_id,
            customer_id=customer_id,
            no_show_date=no_show_date
        )
        self.db.add(no_show_log)
        self.db.commit()
        self.db.refresh(no_show_log)
        return no_show_log

    def get_no_show_log(self, no_show_id: int) -> Optional[NoShowLog]:
        return self.db.query(NoShowLog).filter(NoShowLog.no_show_id == no_show_id).first()

    def update_no_show_log(self, no_show_id: int, data: Dict[str, Any]) -> Optional[WaitingList]:
        no_show_log = self.get_no_show_log(no_show_id)
        if no_show_log:
            for key, value in data.items():
                setattr(no_show_log, key, value)
            self.db.commit()
            self.db.refresh(no_show_log)
        return no_show_log

    def delete_no_show_log(self, no_show_id: int) -> bool:
        no_show_log = self.get_no_show_log(no_show_id)
        if no_show_log:
            self.db.delete(no_show_log)
            self.db.commit()
            return True
        return False
    
    # Policy type CRUD
    def create_policy_type(self, type_name: str, description: str) -> PolicyType:
        policy_type = PolicyType(
            type_name=type_name,
            description=description
        )
        self.db.add(policy_type)
        self.db.commit()
        self.db.refresh(policy_type)
        return policy_type

    def get_policy_type(self, policy_type_id: int) -> Optional[PolicyType]:
        return self.db.query(PolicyType).filter(PolicyType.policy_type_id == policy_type_id).first()

    def update_policy_type(self, policy_type_id: int, data: Dict[str, Any]) -> Optional[PolicyType]:
        policy_type = self.get_policy_type(policy_type_id)
        if policy_type:
            for key, value in data.items():
                setattr(policy_type, key, value)
            self.db.commit()
            self.db.refresh(policy_type)
        return policy_type

    def delete_policy_type(self, policy_type_id: int) -> bool:
        policy_type = self.get_policy_type(policy_type_id)
        if policy_type:
            self.db.delete(policy_type)
            self.db.commit()
            return True
        return False
    
    # Policy CRUD
    def create_policy(self, policy_type_id: int, branch_id: int, name: str) -> Policy:
        policy = Policy(
            policy_type_id=policy_type_id,
            branch_id=branch_id,
            name=name
        )
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy

    def get_policy(self, policy_id: int) -> Optional[Policy]:
        return self.db.query(Policy).filter(Policy.policy_id == policy_id).first()

    def update_policy(self, policy_id: int, data: Dict[str, Any]) -> Optional[Policy]:
        policy = self.get_policy(policy_id)
        if policy:
            for key, value in data.items():
                setattr(policy, key, value)
            self.db.commit()
            self.db.refresh(policy)
        return policy

    def delete_policy(self, policy_id: int) -> bool:
        policy = self.get_policy(policy_id)
        if policy:
            self.db.delete(policy)
            self.db.commit()
            return True
        return False
    
    # Policy details CRUD
    def create_policy_details(self, policy_id: int, details: Dict[str, Any]) -> PolicyDetail:
        policy_details = PolicyDetail(
            policy_id=policy_id,
            details=details
        )
        self.db.add(policy_details)
        self.db.commit()
        self.db.refresh(policy_details)
        return policy_details

    def get_policy_details(self, detail_id: int) -> Optional[PolicyDetail]:
        return self.db.query(PolicyDetail).filter(PolicyDetail.detail_id == detail_id).first()
    
    def get_policy_details_by_policy_id(self, policy_id: int) -> Optional[PolicyDetail]:
        return self.db.query(PolicyDetail).filter(PolicyDetail.policy_id == policy_id).first()

    def update_policy_details(self, detail_id: int, data: Dict[str, Any]) -> Optional[PolicyDetail]:
        policy_details = self.get_policy_details(detail_id)
        if policy_details:
            for key, value in data.items():
                setattr(policy_details, key, value)
            self.db.commit()
            self.db.refresh(policy_details)
        return policy_details

    def delete_policy_details(self, detail_id: int) -> bool:
        policy_details = self.get_policy_details(detail_id)
        if policy_details:
            self.db.delete(policy_details)
            self.db.commit()
            return True
        return False