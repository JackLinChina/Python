"""
app/core/response.py — 统一响应体
"""
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel
 
T = TypeVar("T")
 
 
class ResponseModel(BaseModel, Generic[T]):
    """统一 API 响应格式：{ code, message, data }"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
 
    @classmethod
    def ok(cls, data: T = None, message: str = "操作成功"):
        return cls(code=200, message=message, data=data)
 
    @classmethod
    def fail(cls, message: str = "操作失败", code: int = 400):
        return cls(code=code, message=message, data=None)
 
 
class PageResult(BaseModel, Generic[T]):
    """分页响应结构"""
    items: List[T]  
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """
    分页响应格式（顶层包含分页信息）
    
    格式：
    {
        "code": 0,
        "message": "ok",
        "data": [...],
        "total": 100,
        "page": 1,
        "page_size": 10,
        "total_pages": 10
    }
    """
    code: int = 200
    message: str = "success"
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def ok(cls, data: List[T], total: int, page: int, page_size: int, message: str = "操作成功"):
        import math
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        return cls(
            code=200,
            message=message,
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )