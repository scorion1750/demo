from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from app.schemas.response import ErrorResponseModel

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponseModel(
            code=exc.status_code,
            msg=exc.detail,
            data=None
        ).dict()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponseModel(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            msg="数据验证错误",
            data=exc.errors()
        ).dict()
    )

async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponseModel(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg=f"服务器内部错误: {str(exc)}",
            data=None
        ).dict()
    ) 