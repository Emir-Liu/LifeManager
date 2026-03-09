"""Admin API Router
管理员 API 路由"""
from fastapi import APIRouter

from app.api.v1.admin import conversations

admin_router = APIRouter(prefix="/admin")

# 注册管理员路由
admin_router.include_router(conversations.router)
