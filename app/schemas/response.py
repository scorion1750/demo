from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class StandardResponse(GenericModel, Generic[T]):
    code: int = Field(200, description="状态码")
    msg: str = Field("", description="消息")
    data: Optional[T] = Field(None, description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "",
                "data": {}
            }
        }

# 为了向后兼容，保留 ResponseModel 类
ResponseModel = StandardResponse

class ErrorResponseModel(BaseModel):
    """错误响应模型"""
    code: int
    msg: str
    data: None = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "msg": "Bad Request",
                "data": None
            }
        } 