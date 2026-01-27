"""
统一响应格式
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

# 泛型类型
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""

    code: int = Field(0, description="状态码，0表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "success",
                "data": {}
            }
        }

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "success"):
        """成功响应"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Optional[T] = None):
        """错误响应"""
        return cls(code=code, message=message, data=data)
