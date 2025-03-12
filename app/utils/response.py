from fastapi import HTTPException
from app.schemas.response import ResponseModel

def error_response(status_code: int, detail: str):
    """创建错误响应"""
    return HTTPException(
        status_code=status_code,
        detail=detail
    ) 