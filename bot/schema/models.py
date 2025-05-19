# BOOKINGTABLE/bot/core/models.py
from sqlalchemy import (Column, Integer, String, 
                        Text, Boolean, Date, Time, 
                        DateTime, ForeignKey, CheckConstraint, DECIMAL, JSON, MetaData)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from bot.utils.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = (
        {"schema": "public"}
    )
    
    restaurant_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False) 
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    embedding = relationship(
        "RestaurantEmbedding", 
        back_populates="restaurant", 
        cascade="all, delete-orphan"
    )
    
    branches = relationship("RestaurantBranch", back_populates="restaurant", cascade="all, delete-orphan", lazy='dynamic')
    

class RestaurantBranch(Base):
    __tablename__ = "restaurant_branches"
    __table_args__ = (
        CheckConstraint("max_capacity > 0", name="check_max_capacity_positive"),
        {"schema": "public"}
    )
    
    branch_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("public.restaurants.restaurant_id", ondelete="CASCADE"), nullable=False, index=True)
    address = Column(Text, nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    restaurant = relationship("Restaurant", back_populates="branches")
    service_types = relationship("ServiceType", back_populates="branch", cascade="all, delete-orphan", lazy='noload')
    tables = relationship("Table", back_populates="branch", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="branch", cascade="all, delete-orphan")
    waiting_lists = relationship("WaitingList", back_populates="branch", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="branch", cascade="all, delete-orphan")
    

class ServiceType(Base):
    __tablename__ = "service_types"
    __table_args__ = (
        CheckConstraint(
            "service_name IN ('Dine-In', 'Takeaway', 'Delivery', 'Buffet', 'Catering', "
            "'Private Dining', 'Outdoor Seating', 'Bar Service')",
            name="check_service_name"
        ),
        {"schema": "public"}
    )
    
    service_id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("public.restaurant_branches.branch_id", ondelete="CASCADE"))
    service_name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    embedding = relationship(
        "ServiceTypeEmbedding", 
        back_populates="service_type", 
        cascade="all, delete-orphan"
    )
    
    branch = relationship("RestaurantBranch", back_populates="service_types") 

class Table(Base):
    __tablename__ = "tables"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="check_capacity_positive"),
        {"schema": "public"}
    )
    
    table_id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("public.restaurant_branches.branch_id", ondelete="CASCADE"))
    table_number = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    
    branch = relationship("RestaurantBranch", back_populates="tables")  # Thêm relationship ngược
    table_status = relationship("TableStatus", back_populates="table", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="table")
    

class TableStatus(Base):
    __tablename__ = "table_status"
    __table_args__ = (
        CheckConstraint("status IN ('available', 'reserved', 'occupied', 'needs_cleaning')", 
                       name="check_status_value"),
        {"schema": "public"}
    )
    
    status_id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("public.tables.table_id", ondelete="CASCADE"))
    status = Column(String(20), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp())
    
    table = relationship("Table", back_populates="table_status")

class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("party_size > 0", name="check_party_size_positive"),
        CheckConstraint("status IN ('pending', 'confirmed', 'cancelled', 'no_show', 'completed')", 
                       name="check_status_value"),
        {"schema": "public"}
    )
    
    reservation_id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("public.tables.table_id", ondelete="SET NULL"))
    customer_id = Column(Integer, ForeignKey("public.customers.customer_id", ondelete="SET NULL"))
    branch_id = Column(Integer, ForeignKey("public.restaurant_branches.branch_id", ondelete="CASCADE"))
    policy_id = Column(Integer, ForeignKey("public.policies.policy_id", ondelete="SET NULL"))
    
    reservation_date = Column(Date, nullable=False)
    reservation_time = Column(Time, nullable=False)
    party_size = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    confirmed_at = Column(DateTime)
    reminder_sent = Column(Boolean, default=False)
    note = Column(String, nullable=True)
    
    table = relationship("Table", back_populates="reservations")
    customer = relationship("Customer", back_populates="reservations")
    branch = relationship("RestaurantBranch", back_populates="reservations")
    policy = relationship("Policy", back_populates="reservations")
    logs = relationship("ReservationLog", back_populates="reservation", cascade="all, delete-orphan")
    history = relationship("ReservationHistory", back_populates="reservation")
    payments = relationship("Payment", back_populates="reservation", cascade="all, delete-orphan")
    no_shows = relationship("NoShowLog", back_populates="reservation", cascade="all, delete-orphan")
    

class ReservationLog(Base):
    __tablename__ = "reservation_logs"
    __table_args__ = (
        CheckConstraint(
            "action IN ('created', 'confirmed', 'cancelled', 'modified', 'reminder_sent', 'no_show')",
            name="check_action_value"
        ),
        {"schema": "public"}
    )
    
    log_id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("public.reservations.reservation_id", ondelete="CASCADE"))
    action = Column(String(50), nullable=False)
    action_timestamp = Column(DateTime, default=func.current_timestamp())
    details = Column(Text)
    
    reservation = relationship("Reservation", back_populates="logs") 

class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (
        {"schema": "public"}
    )
    
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    salutation = Column(String(20), nullable=True)
    psid = Column(String(255), unique=True, nullable=True)
    is_vip = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    reservations = relationship("Reservation", back_populates="customer")
    histories = relationship("ReservationHistory", back_populates="customer", cascade="all, delete-orphan")
    waiting_lists = relationship("WaitingList", back_populates="customer", cascade="all, delete-orphan")
    no_shows = relationship("NoShowLog", back_populates="customer", cascade="all, delete-orphan")

class ReservationHistory(Base):
    __tablename__ = "reservation_history"
    __table_args__ = (
        CheckConstraint("status IN ('confirmed', 'cancelled', 'no_show', 'completed')", 
                       name="check_status_value"),
        {"schema": "public"}
    )
    
    history_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("public.customers.customer_id", ondelete="CASCADE"))
    reservation_id = Column(Integer, ForeignKey("public.reservations.reservation_id", ondelete="SET NULL"))
    reservation_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    customer = relationship("Customer", back_populates="histories")
    reservation = relationship("Reservation", back_populates="history")
    
    
class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="check_amount_non_negative"),
        CheckConstraint("payment_method IN ('cash', 'momo', 'zalopay', 'visa')", 
                       name="check_payment_method"),
        CheckConstraint("payment_status IN ('pending', 'completed', 'failed')", 
                       name="check_payment_status"),
        {"schema": "public"}
    )
    
    payment_id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("public.reservations.reservation_id", ondelete="CASCADE"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(50), default="cash")
    payment_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=func.current_timestamp())
    
    reservation = relationship("Reservation", back_populates="payments")

class WaitingList(Base):
    __tablename__ = "waiting_list"
    __table_args__ = (
        CheckConstraint("party_size > 0", name="check_party_size_positive"),
        CheckConstraint("status IN ('waiting', 'notified', 'cancelled', 'seated')", 
                       name="check_status_value"),
        {"schema": "public"}
    )
    
    wait_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("public.customers.customer_id", ondelete="CASCADE"))
    branch_id = Column(Integer, ForeignKey("public.restaurant_branches.branch_id", ondelete="CASCADE"))
    requested_date = Column(Date, nullable=False)
    requested_time = Column(Time, nullable=False)
    party_size = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    customer = relationship("Customer", back_populates="waiting_lists")
    branch = relationship("RestaurantBranch", back_populates="waiting_lists")
    

class NoShowLog(Base):
    __tablename__ = "no_show_logs"
    __table_args__ = (
        {"schema": "public"}
    )
    
    no_show_id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("public.reservations.reservation_id", ondelete="CASCADE"))
    customer_id = Column(Integer, ForeignKey("public.customers.customer_id", ondelete="CASCADE"))
    no_show_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    reservation = relationship("Reservation", back_populates="no_shows")
    customer = relationship("Customer", back_populates="no_shows")

class PolicyType(Base):
    __tablename__ = "policy_types"
    __table_args__ = (
        CheckConstraint(
            "type_name IN ('Cancellation', 'Deposit', 'Dress Code', 'Late Arrival', 'No Show', "
            "'Reservation Time Limit', 'Minimum Spend', 'Group Size')",
            name="check_policy_type_name"
        ),
        {"schema": "public"}
    )
    
    policy_type_id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    policies = relationship("Policy", back_populates="policy_type")

class Policy(Base):
    __tablename__ = "policies"
    __table_args__ = (
        {"schema": "public"}
    )
    
    policy_id = Column(Integer, primary_key=True, index=True)
    policy_type_id = Column(Integer, ForeignKey("public.policy_types.policy_type_id", ondelete="RESTRICT"))
    branch_id = Column(Integer, ForeignKey("public.restaurant_branches.branch_id", ondelete="CASCADE"))
    
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    embedding = relationship(
        "PolicyEmbedding", 
        back_populates="policy", 
        cascade="all, delete-orphan"
    )
    
    policy_type = relationship("PolicyType", back_populates="policies")
    branch = relationship("RestaurantBranch", back_populates="policies")
    details = relationship("PolicyDetail", back_populates="policy", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="policy")

class PolicyDetail(Base):
    __tablename__ = "policy_details"
    __table_args__ = (
        {"schema": "public"}
    )
    
    detail_id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("public.policies.policy_id", ondelete="CASCADE"))
    details = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    embedding = relationship(
        "PolicyDetailsEmbedding",
        back_populates="policy_detail",
        cascade="all, delete-orphan"
    )
    
    policy = relationship("Policy", back_populates="details")