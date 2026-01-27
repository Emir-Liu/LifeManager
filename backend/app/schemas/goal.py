"""
目标相关的 Pydantic Schema
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GoalBase(BaseModel):
    """目标基础 Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="目标标题")
    description: Optional[str] = Field(None, description="目标描述")
    deadline: Optional[date] = Field(None, description="截止日期")


class GoalCreate(GoalBase):
    """创建目标请求"""
    pass


class GoalUpdate(BaseModel):
    """更新目标请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(planning|confirmed|completed)$")


class GoalResponse(BaseModel):
    """目标响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class GoalDetailResponse(GoalResponse):
    """目标详情响应（包含统计信息）"""
    tasks_count: int = Field(default=0, description="任务总数")
    completed_tasks: int = Field(default=0, description="已完成任务数")
