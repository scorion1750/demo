from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RepeatType(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    repeat_type: RepeatType = RepeatType.NONE
    coins_reward: int = Field(default=0, ge=0)
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    repeat_type: Optional[RepeatType] = None
    coins_reward: Optional[int] = None
    due_date: Optional[datetime] = None
    
    @validator('coins_reward')
    def coins_reward_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Coins reward cannot be negative')
        return v
    
    class Config:
        from_attributes = True

class TaskInDB(TaskBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDB):
    pass

class TaskCompletionBase(BaseModel):
    task_id: int

class TaskCompletionCreate(TaskCompletionBase):
    pass

class TaskCompletionInDB(TaskCompletionBase):
    id: int
    user_id: int
    completed_at: datetime

    class Config:
        from_attributes = True

class TaskCompletion(TaskCompletionInDB):
    pass 