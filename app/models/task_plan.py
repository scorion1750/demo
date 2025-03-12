from sqlalchemy import Boolean, Column, Integer, String, DateTime, BigInteger, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.task import RepeatType
from app.database import Base

class TaskPlanStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class TaskPlan(Base):
    __tablename__ = "task_plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    repeat_type = Column(Enum(RepeatType), default=RepeatType.NONE)
    coins_reward = Column(BigInteger, default=0)
    status = Column(Enum(TaskPlanStatus), default=TaskPlanStatus.ACTIVE)
    start_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)  # 可选的结束日期
    last_generated = Column(DateTime(timezone=True), nullable=True)  # 上次生成任务的时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="task_plans")
    tasks = relationship("Task", back_populates="task_plan") 