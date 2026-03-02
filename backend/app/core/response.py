"""
统一响应格式
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field, ConfigDict

# 泛型类型
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 0,
                "message": "success",
                "data": {}
            }
        }
    )

    code: int = Field(0, description="状态码，0表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "success"):
        """成功响应"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Optional[T] = None):
        """错误响应"""
        return cls(code=code, message=message, data=data)


def success_response(data: Optional[T] = None, message: str = "success") -> ApiResponse[T]:
    """
    成功响应辅助函数

    Args:
        data: 响应数据
        message: 响应消息

    Returns:
        ApiResponse 实例
    """
    return ApiResponse.success(data=data, message=message)


def error_response(code: int, message: str, data: Optional[T] = None) -> ApiResponse[T]:
    """
    错误响应辅助函数

    Args:
        code: 错误码
        message: 错误消息
        data: 响应数据

    Returns:
        ApiResponse 实例
    """
    return ApiResponse.error(code=code, message=message, data=data)
