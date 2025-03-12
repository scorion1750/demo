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
import socket
from app.utils.ip import get_client_ip
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 从环境变量获取端口，默认为8001
PORT = int(os.getenv("API_PORT", 8001))

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

# 获取本机 IP 地址
def get_local_ip():
    try:
        # 创建一个临时 socket 连接来获取本机 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个外部服务器（不需要真正发送数据）
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.error(f"获取本地 IP 地址时出错: {e}")
        return "127.0.0.1"  # 默认返回 localhost

# 在应用启动时显示 IP 地址
@app.on_event("startup")
async def startup_event():
    local_ip = get_local_ip()
    logger.info(f"服务器启动成功！")
    logger.info(f"本地 IP 地址: {local_ip}")
    logger.info(f"监听端口: {PORT}")
    logger.info(f"API 文档可通过以下地址访问:")
    logger.info(f"Swagger UI: http://{local_ip}:{PORT}/docs")
    logger.info(f"ReDoc: http://{local_ip}:{PORT}/redoc")
    
    # # 尝试检测网络连接
    # try:
    #     import socket
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     s.bind((local_ip, PORT))
    #     s.close()
    #     logger.info(f"端口 {PORT} 可用并已成功绑定")
    # except Exception as e:
    #     logger.error(f"端口绑定测试失败: {e}")

# 修改会话中间件，记录客户端 IP
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    """会话管理中间件"""
    # 获取客户端真实 IP
    client_ip = get_client_ip(request)
    
    # 记录请求信息
    logger.info(f"请求来自 IP: {client_ip} | 路径: {request.url.path} | 方法: {request.method}")
    
    # 处理请求
    response = await call_next(request)
    
    # 记录响应状态
    logger.info(f"响应状态: {response.status_code} | 客户端 IP: {client_ip}")
    
    return response

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",  port=PORT, reload=False) 