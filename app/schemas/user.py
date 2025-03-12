from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str
    email: str
    coins: Optional[int] = 0
    
    @validator('email')
    def email_must_be_valid(cls, v):
        # 简单的电子邮件验证
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    coins: int = Field(default=0, ge=0)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    coins: Optional[int] = None
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('coins')
    def coins_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Coins cannot be negative')
        return v
    
    # 确保 dict() 方法正确处理
    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs)
    
    class Config:
        orm_mode = True

class UserInDB(UserBase):
    id: int
    is_active: bool
    coins: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    coins: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 