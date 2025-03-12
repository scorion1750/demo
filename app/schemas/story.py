from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

class StoryType(str, Enum):
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    SCIFI = "scifi"
    FANTASY = "fantasy"
    HORROR = "horror"

# 故事选择
class StoryChoiceBase(BaseModel):
    text: str
    next_chapter_id: Optional[int] = None

class StoryChoiceCreate(StoryChoiceBase):
    pass

class StoryChoiceUpdate(StoryChoiceBase):
    text: Optional[str] = None

class StoryChoiceInDB(StoryChoiceBase):
    id: int
    chapter_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class StoryChoice(StoryChoiceInDB):
    pass

# 故事章节
class StoryChapterBase(BaseModel):
    story_id: int
    title: str
    content: str
    order_num: int = 0

class StoryChapterCreate(StoryChapterBase):
    pass

class StoryChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order_num: Optional[int] = None

class StoryChapterInDB(StoryChapterBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class StoryChapter(StoryChapterInDB):
    choices: List[StoryChoice] = []

# 故事
class StoryBase(BaseModel):
    title: str
    description: Optional[str] = None
    story_type: StoryType = StoryType.ADVENTURE
    unlock_cost: int = Field(default=5000, ge=0)
    is_active: bool = True

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    story_type: Optional[StoryType] = None
    unlock_cost: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('unlock_cost')
    def unlock_cost_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Unlock cost cannot be negative')
        return v

class StoryInDB(StoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Story(StoryInDB):
    chapters: List[StoryChapter] = []

# 用户故事响应
class UserStoryResponseBase(BaseModel):
    chapter_id: int
    choice_id: Optional[int] = None
    custom_response: Optional[str] = None

class UserStoryResponseCreate(UserStoryResponseBase):
    pass

class UserStoryResponseInDB(UserStoryResponseBase):
    id: int
    user_story_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserStoryResponse(UserStoryResponseInDB):
    pass

# 用户故事
class UserStoryBase(BaseModel):
    story_id: int
    current_chapter_id: Optional[int] = None
    is_completed: bool = False

class UserStoryCreate(UserStoryBase):
    pass

class UserStoryUpdate(BaseModel):
    current_chapter_id: Optional[int] = None
    is_completed: Optional[bool] = None

class UserStoryInDB(UserStoryBase):
    id: int
    user_id: int
    unlocked_at: datetime
    last_interaction: datetime

    class Config:
        from_attributes = True

class UserStory(UserStoryInDB):
    responses: List[UserStoryResponse] = []
    story: Optional[Story] = None
    current_chapter: Optional[StoryChapter] = None

    class Config:
        from_attributes = True
        # 允许额外字段
        extra = "allow"
        # 允许部分初始化
        validate_assignment = False 