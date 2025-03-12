from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.schemas.task import RepeatType, Task as TaskSchema

class TaskPlanStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class TaskPlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    repeat_type: RepeatType = RepeatType.NONE
    coins_reward: int = Field(default=0, ge=0)
    status: TaskPlanStatus = TaskPlanStatus.ACTIVE
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = None

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class TaskPlanCreate(TaskPlanBase):
    pass

class TaskPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    repeat_type: Optional[RepeatType] = None
    coins_reward: Optional[int] = None
    status: Optional[TaskPlanStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('coins_reward')
    def coins_reward_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Coins reward cannot be negative')
        return v
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class TaskPlanInDB(TaskPlanBase):
    id: int
    user_id: int
    last_generated: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskPlan(TaskPlanInDB):
    tasks: List[TaskSchema] = []

    class Config:
        from_attributes = True

class TaskPlanWithInitialTask(BaseModel):
    task_plan: TaskPlan
    initial_task: Optional[TaskSchema] = None

    class Config:
        from_attributes = True 