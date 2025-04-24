# BOOKINGTABLE/bot/core/vector_models.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, MetaData
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector  # Dùng để lưu vector trong PostgreSQL
from bot.utils.database import Base  # Dùng Base từ database.py
from bot.schema.models import Restaurant, ServiceType, Policy, PolicyDetail  

# Định nghĩa metadata cho schema vector_schema
metadata = MetaData(schema='vector_schema')

class RestaurantEmbedding(Base):
    __tablename__ = "restaurant_embeddings"
    __table_args__ = {"schema": "vector_schema"}  # Lưu trong schema vector_schema

    embedding_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(
        Integer, 
        ForeignKey("public.restaurants.restaurant_id", ondelete="CASCADE")
    )
    embedding = Column(Vector(768))  # Vector 768 chiều, tùy chỉnh theo model embedding
    created_at = Column(DateTime, default=func.current_timestamp())
    
    restaurant = relationship(
        "Restaurant", 
        back_populates="embedding"
    )
    
    # Phương thức để tìm kiếm vector gần nhất
    @classmethod
    def find_similar(cls, session, query_vector, limit=5):
        """Tìm các restaurant có embedding gần với query_vector"""
        return session.query(cls, Restaurant).join(
            Restaurant, cls.restaurant_id == Restaurant.restaurant_id
        ).order_by(
            cls.embedding.cosine_distance(query_vector)
        ).limit(limit).all()

class ServiceTypeEmbedding(Base):
    __tablename__ = "servcie_type_embeddings"
    __table_args__ = {"schema": "vector_schema"}

    embedding_id = Column(Integer, primary_key=True, index=True)
    service_id = Column(
        Integer, 
        ForeignKey("public.service_types.service_id", ondelete="CASCADE")
    )
    embedding = Column(Vector(768))
    created_at = Column(DateTime, default=func.current_timestamp())
    
    service_type = relationship(
        "ServiceType", 
        back_populates="embedding"
    )
    
    # Phương thức để tìm kiếm vector gần nhất
    @classmethod
    def find_similar(cls, session, query_vector, limit=5):
        """Tìm các table có embedding gần với query_vector"""
        return session.query(cls, ServiceType).join(
            ServiceType, cls.service_id == ServiceType.service_id
        ).order_by(
            cls.embedding.cosine_distance(query_vector)
        ).limit(limit).all()

class PolicyEmbedding(Base):
    __tablename__ = "policy_embeddings"
    __table_args__ = {"schema": "vector_schema"}

    embedding_id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(
        Integer, 
        ForeignKey("public.policies.policy_id", ondelete="CASCADE")
    )
    embedding = Column(Vector(768))
    created_at = Column(DateTime, default=func.current_timestamp())
    
    policy = relationship(
        "Policy", 
        back_populates="embedding"
    )
    
    # Phương thức để tìm kiếm vector gần nhất
    @classmethod
    def find_similar(cls, session, query_vector, limit=5):
        """Tìm các reservation có embedding gần với query_vector"""
        return session.query(cls, Policy).join(
            Policy, cls.policy_id == Policy.policy_id
        ).order_by(
            cls.embedding.cosine_distance(query_vector)
        ).limit(limit).all()

class PolicyDetailsEmbedding(Base):
    __tablename__ = "policy_details_embeddings"
    __table_args__ = {"schema": "vector_schema"}

    embedding_id = Column(Integer, primary_key=True, index=True)
    policy_detail_id = Column(
        Integer, 
        ForeignKey("public.policy_details.detail_id", ondelete="CASCADE")
    )
    embedding = Column(Vector(768))
    created_at = Column(DateTime, default=func.current_timestamp())
    
    policy_detail = relationship(
        "PolicyDetail", 
        back_populates="embedding"
    )
    
    # Phương thức để tìm kiếm vector gần nhất
    @classmethod
    def find_similar(cls, session, query_vector, limit=5):
        """Tìm các reservation có embedding gần với query_vector"""
        return session.query(cls, PolicyDetail).join(
            PolicyDetail, cls.detail_id == PolicyDetail.detail_id
        ).order_by(
            cls.embedding.cosine_distance(query_vector)
        ).limit(limit).all()
