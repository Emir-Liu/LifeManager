"""
用户相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """更新用户信息"""
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserResponse(UserBase):
    """用户响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class Token(BaseModel):
    """令牌响应"""
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    token: str
    refresh_token: str


class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: Optional[int] = None  # 用户ID
