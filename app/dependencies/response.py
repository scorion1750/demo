from typing import TypeVar, Generic, Callable
from fastapi import Depends
from app.schemas.response import ResponseModel

T = TypeVar('T')

class ResponseDependency(Generic[T]):
    def __init__(self, response_model: T):
        self.response_model = response_model
    
    def __call__(self, data: T):
        return ResponseModel(data=data) 