from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    code_reviews = relationship("CodeReview", back_populates="user")
    shared_snippets = relationship("SharedSnippet", back_populates="user")

class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(Text)
    language = Column(String)
    review_data = Column(Text)  # JSON string of review results
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)
    
    # Relationships
    user = relationship("User", back_populates="code_reviews")
    performance_metrics = relationship("PerformanceMetric", back_populates="code_review")

class SharedSnippet(Base):
    __tablename__ = "shared_snippets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(Text)
    language = Column(String)
    title = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="shared_snippets")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    code_review_id = Column(Integer, ForeignKey("code_reviews.id"))
    metric_name = Column(String)
    metric_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    code_review = relationship("CodeReview", back_populates="performance_metrics") 