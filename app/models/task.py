from sqlalchemy import Boolean, Column, Integer, String, DateTime, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class RepeatType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False)
    repeat_type = Column(Enum(RepeatType), default=RepeatType.NONE)
    coins_reward = Column(BigInteger, default=0)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    task_plan_id = Column(Integer, ForeignKey("task_plans.id", ondelete="SET NULL"), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="tasks")
    completions = relationship("TaskCompletion", back_populates="task", cascade="all, delete-orphan")
    task_plan = relationship("TaskPlan", back_populates="tasks") 