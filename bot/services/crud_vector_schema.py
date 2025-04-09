# BOOKINGTABLE/bot/services/crud_vector_schema.py
from sqlalchemy.orm import Session
from bot.schema.vector_models import (RestaurantEmbedding, ServiceTypeEmbedding, 
                                    PolicyEmbedding, PolicyDetailsEmbedding)
from typing import List, Optional

# CRUD cho schema vector_schema
class VectorCRUD:
    def __init__(self, db: Session):
        self.db = db

    # RestaurantEmbedding CRUD
    def create_restaurant_embedding(self, restaurant_id: int, embedding: List[float]) -> RestaurantEmbedding:
        embedding_obj = RestaurantEmbedding(restaurant_id=restaurant_id, embedding=embedding)
        self.db.add(embedding_obj)
        self.db.commit()
        self.db.refresh(embedding_obj)
        return embedding_obj

    def get_restaurant_embedding(self, embedding_id: int) -> Optional[RestaurantEmbedding]:
        return self.db.query(RestaurantEmbedding).filter(RestaurantEmbedding.embedding_id == embedding_id).first()

    def find_similar_restaurants(self, query_vector: List[float], limit: int = 5) -> List:
        return RestaurantEmbedding.find_similar(self.db, query_vector, limit)

    def update_restaurant_embedding(self, embedding_id: int, embedding: List[float]) -> Optional[RestaurantEmbedding]:
        embedding_obj = self.get_restaurant_embedding(embedding_id)
        if embedding_obj:
            embedding_obj.embedding = embedding
            self.db.commit()
            self.db.refresh(embedding_obj)
        return embedding_obj

    def delete_restaurant_embedding(self, embedding_id: int) -> bool:
        embedding_obj = self.get_restaurant_embedding(embedding_id)
        if embedding_obj:
            self.db.delete(embedding_obj)
            self.db.commit()
            return True
        return False
    
    # ServiceTypeEmbedding CRUD
    def create_service_type_embedding(self, service_id: int, embedding: List[float]) -> ServiceTypeEmbedding:
        embedding_obj = ServiceTypeEmbedding(service_id=service_id, embedding=embedding)
        self.db.add(embedding_obj)
        self.db.commit()
        self.db.refresh(embedding_obj)
        return embedding_obj

    def get_service_type_embedding(self, embedding_id: int) -> Optional[ServiceTypeEmbedding]:
        return self.db.query(RestaurantEmbedding).filter(ServiceTypeEmbedding.embedding_id == embedding_id).first()

    def find_similar_service_type(self, query_vector: List[float], limit: int = 5) -> List:
        return ServiceTypeEmbedding.find_similar(self.db, query_vector, limit)

    def update_service_type_embedding(self, embedding_id: int, embedding: List[float]) -> Optional[ServiceTypeEmbedding]:
        embedding_obj = self.get_service_type_embedding(embedding_id)
        if embedding_obj:
            embedding_obj.embedding = embedding
            self.db.commit()
            self.db.refresh(embedding_obj)
        return embedding_obj

    def delete_service_type_embedding(self, embedding_id: int) -> bool:
        embedding_obj = self.get_service_type_embedding(embedding_id)
        if embedding_obj:
            self.db.delete(embedding_obj)
            self.db.commit()
            return True
        return False
    
    # PolicyEmbedding CRUD
    def create_policy_embedding(self, policy_id: int, embedding: List[float]) -> PolicyEmbedding:
        embedding_obj = PolicyEmbedding(policy_id=policy_id, embedding=embedding)
        self.db.add(embedding_obj)
        self.db.commit()
        self.db.refresh(embedding_obj)
        return embedding_obj

    def get_policy_embedding(self, embedding_id: int) -> Optional[PolicyEmbedding]:
        return self.db.query(PolicyEmbedding).filter(PolicyEmbedding.embedding_id == embedding_id).first()

    def find_similar_policy(self, query_vector: List[float], limit: int = 5) -> List:
        return PolicyEmbedding.find_similar(self.db, query_vector, limit)

    def update_policy_embedding(self, embedding_id: int, embedding: List[float]) -> Optional[PolicyEmbedding]:
        embedding_obj = self.get_policy_embedding(embedding_id)
        if embedding_obj:
            embedding_obj.embedding = embedding
            self.db.commit()
            self.db.refresh(embedding_obj)
        return embedding_obj

    def delete_policy_embedding(self, embedding_id: int) -> bool:
        embedding_obj = self.get_policy_embedding(embedding_id)
        if embedding_obj:
            self.db.delete(embedding_obj)
            self.db.commit()
            return True
        return False
    
    # PolicyDetailsEmbedding CRUD
    def create_policy_details_embedding(self, policy_detail_id: int, embedding: List[float]) -> PolicyDetailsEmbedding:
        embedding_obj = PolicyDetailsEmbedding(policy_detail_id=policy_detail_id, embedding=embedding)
        self.db.add(embedding_obj)
        self.db.commit()
        self.db.refresh(embedding_obj)
        return embedding_obj

    def get_policy_details_embedding(self, embedding_id: int) -> Optional[PolicyDetailsEmbedding]:
        return self.db.query(PolicyDetailsEmbedding).filter(PolicyDetailsEmbedding.embedding_id == embedding_id).first()

    def find_similar_policy_details(self, query_vector: List[float], limit: int = 5) -> List:
        return PolicyDetailsEmbedding.find_similar(self.db, query_vector, limit)

    def update_policy_details_embedding(self, embedding_id: int, embedding: List[float]) -> Optional[PolicyDetailsEmbedding]:
        embedding_obj = self.get_policy_details_embedding(embedding_id)
        if embedding_obj:
            embedding_obj.embedding = embedding
            self.db.commit()
            self.db.refresh(embedding_obj)
        return embedding_obj

    def delete_policy_details_embedding(self, embedding_id: int) -> bool:
        embedding_obj = self.get_policy_details_embedding(embedding_id)
        if embedding_obj:
            self.db.delete(embedding_obj)
            self.db.commit()
            return True
        return False