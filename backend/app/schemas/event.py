"""
Event Schemas
日程相关的 Pydantic Schema
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# 枚举定义
class EventType(str, Enum):
    """日程类型"""
    MEETING = "meeting"
    COURSE = "course"
    REMINDER = "reminder"
    GENERAL = "general"


# 日程相关 Schema
class EventBase(BaseModel):
    """日程基础模型"""
    title: str = Field(..., max_length=200, description="日程标题")
    description: Optional[str] = Field(None, description="日程描述")
    event_type: EventType = Field(default=EventType.GENERAL, description="日程类型")
    start_date: datetime = Field(..., description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    duration_minutes: int = Field(..., gt=0, description="持续时间(分钟)")
    recurrence_rules: Optional[dict] = Field(None, description="重复规则")
    color: str = Field(default="#666666", pattern=r"^#[0-9A-Fa-f]{6}$", description="十六进制颜色")
    is_active: bool = Field(default=True, description="是否激活")


class EventCreate(EventBase):
    """创建日程"""
    pass


class EventUpdate(BaseModel):
    """更新日程"""
    title: Optional[str] = Field(None, max_length=200, description="日程标题")
    description: Optional[str] = Field(None, description="日程描述")
    event_type: Optional[EventType] = Field(None, description="日程类型")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration_minutes: Optional[int] = Field(None, gt=0, description="持续时间(分钟)")
    recurrence_rules: Optional[dict] = Field(None, description="重复规则")
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="十六进制颜色")
    is_active: Optional[bool] = Field(None, description="是否激活")


class EventResponse(EventBase):
    """日程响应"""
    id: int
    user_id: int
    parent_event_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """日程列表响应"""
    total: int
    items: list[EventResponse]
