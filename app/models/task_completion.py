from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    task = relationship("Task", back_populates="completions")
    user = relationship("User") 