"""
API v1 Router
Phase 2 新增的 API 端点
"""
from fastapi import APIRouter

from app.api.v1 import conversations, events, timeline, time_preferences

api_router = APIRouter()

# 注册各个路由 (注意：这里只包含 Phase 2 新增的 API)
api_router.include_router(conversations.router, tags=["Conversations"])
api_router.include_router(events.router, tags=["Events"])
api_router.include_router(time_preferences.router, tags=["Time Preferences"])
api_router.include_router(timeline.router, tags=["Timeline"])
