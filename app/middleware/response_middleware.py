import json
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.schemas.response import ResponseModel
import logging
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 记录请求路径
        logger.info(f"Processing request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # 记录响应类型
        logger.info(f"Response type: {type(response)}")
        
        # 如果是 JSONResponse 且不是错误响应
        if isinstance(response, JSONResponse) and response.status_code < 400:
            try:
                # 获取原始响应数据
                response_body = response.body.decode()
                logger.info(f"Response body: {response_body}")
                
                response_content = json.loads(response_body)
                logger.info(f"Response content: {response_content}")
                
                # 检查是否已经是标准格式
                if isinstance(response_content, dict) and all(key in response_content for key in ["code", "msg", "data"]):
                    logger.info("Response already in standard format")
                    
                    # 确保 coins 字段是整数
                    if "data" in response_content and isinstance(response_content["data"], dict) and "coins" in response_content["data"]:
                        if response_content["data"]["coins"] is None:
                            response_content["data"]["coins"] = 0
                    
                    return response
                
                # 创建新的响应
                new_content = {
                    "code": response.status_code,
                    "msg": "",
                    "data": response_content
                }
                logger.info(f"New content: {new_content}")
                
                # 创建新的 JSONResponse
                new_response = JSONResponse(
                    content=new_content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
                return new_response
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                return response
        
        logger.info("Response not processed by middleware")
        return response 