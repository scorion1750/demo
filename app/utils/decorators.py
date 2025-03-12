from functools import wraps
from app.schemas.response import ResponseModel

def response_wrapper(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if isinstance(result, ResponseModel):
            return result
        return ResponseModel(data=result)
    return wrapper 