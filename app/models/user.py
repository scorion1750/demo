from sqlalchemy import Boolean, Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    coins = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    user_stories = relationship("UserStory", back_populates="user", cascade="all, delete-orphan")
    task_plans = relationship("TaskPlan", back_populates="user", cascade="all, delete-orphan") 