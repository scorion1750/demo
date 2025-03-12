from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from app.routers import user, task, story, task_plan
from app.database import engine
from app.models import user as user_model, task as task_model, task_completion as task_completion_model
from app.models import story as story_model, task_plan as task_plan_model
from app.utils.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.middleware.response_middleware import ResponseMiddleware
import logging
import traceback
from fastapi import status

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表（如果不存在）
user_model.Base.metadata.create_all(bind=engine)
task_model.Base.metadata.create_all(bind=engine)
task_completion_model.Base.metadata.create_all(bind=engine)
story_model.Base.metadata.create_all(bind=engine)
task_plan_model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="用户管理与任务API",
    description="用于管理用户和任务的API",
    version="0.1.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 添加响应中间件
app.add_middleware(ResponseMiddleware)

# 包含路由
app.include_router(user.router)
app.include_router(task.router)
app.include_router(story.router)
app.include_router(task_plan.router)

# 全局异常处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """统一处理 HTTP 异常，返回标准格式的响应"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "msg": exc.detail,
            "data": None
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """统一处理所有其他异常，返回标准格式的响应"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "Internal Server Error",
            "data": None
        },
    )

@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    """处理响应验证错误，提供更详细的错误信息"""
    logger.error(f"响应验证错误: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "msg": f"服务器响应格式错误: {str(exc)}",
            "data": None
        },
    )

@app.get("/")
def read_root():
    """API根路径，返回欢迎信息"""
    return {"message": "Welcome to User Management and Task API"}

@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    print(f"Request path: {request.url.path}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 