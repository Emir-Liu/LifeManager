"""
用户相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")
    nickname: Optional[str] = Field(None, min_length=1, max_length=100, description="昵称")


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    code: Optional[str] = Field(None, min_length=6, max_length=6, description="验证码")


class UserLogin(BaseModel):
    """用户登录"""
    phone: str = Field(..., min_length=11, max_length=20)
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """更新用户信息"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """用户响应"""
    id: int
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应"""
    user_id: int
    token: str
    refresh_token: str


class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: Optional[int] = None  # 用户ID
