"""
TimePreference Schemas
时间偏好相关的 Pydantic Schema
"""
from datetime import datetime, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# 枚举定义
class SleepType(str, Enum):
    """作息类型"""
    EARLY = "early"
    NORMAL = "normal"
    LATE = "late"


# 时间偏好相关 Schema
class TimePreferenceBase(BaseModel):
    """时间偏好基础模型"""
    sleep_type: SleepType = Field(default=SleepType.NORMAL, description="作息类型")
    wake_up_time: time = Field(default=time(7, 0), description="起床时间")
    sleep_time: time = Field(default=time(23, 0), description="睡眠时间")
    lunch_start: time = Field(default=time(12, 0), description="午餐开始")
    lunch_end: time = Field(default=time(13, 30), description="午餐结束")
    work_start: Optional[time] = Field(None, description="工作开始时间")
    work_end: Optional[time] = Field(None, description="工作结束时间")
    work_days: Optional[str] = Field(default="0,1,2,3,4", description="工作日(0=周一)")
    study_start: Optional[time] = Field(None, description="学习开始时间")
    study_end: Optional[time] = Field(None, description="学习结束时间")
    preferred_task_start: Optional[time] = Field(None, description="首选任务开始时间")
    preferred_task_end: Optional[time] = Field(None, description="首选任务结束时间")
    buffer_time_minutes: int = Field(default=10, ge=0, description="缓冲时间(分钟)")


class TimePreferenceCreate(TimePreferenceBase):
    """创建时间偏好"""
    pass


class TimePreferenceUpdate(BaseModel):
    """更新时间偏好"""
    sleep_type: Optional[SleepType] = Field(None, description="作息类型")
    wake_up_time: Optional[time] = Field(None, description="起床时间")
    sleep_time: Optional[time] = Field(None, description="睡眠时间")
    lunch_start: Optional[time] = Field(None, description="午餐开始")
    lunch_end: Optional[time] = Field(None, description="午餐结束")
    work_start: Optional[time] = Field(None, description="工作开始时间")
    work_end: Optional[time] = Field(None, description="工作结束时间")
    work_days: Optional[str] = Field(None, description="工作日(0=周一)")
    study_start: Optional[time] = Field(None, description="学习开始时间")
    study_end: Optional[time] = Field(None, description="学习结束时间")
    preferred_task_start: Optional[time] = Field(None, description="首选任务开始时间")
    preferred_task_end: Optional[time] = Field(None, description="首选任务结束时间")
    buffer_time_minutes: Optional[int] = Field(None, ge=0, description="缓冲时间(分钟)")


class TimePreferenceResponse(TimePreferenceBase):
    """时间偏好响应"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TimeStatsResponse(BaseModel):
    """时间统计响应"""
    total_hours: float
    goal_hours: dict  # {goal_title: hours}
    task_type_hours: dict  # {task_type: hours}
    date_range: tuple[datetime, datetime]
