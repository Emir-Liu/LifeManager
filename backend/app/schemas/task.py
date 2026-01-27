"""
任务相关的 Pydantic Schema
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    """任务基础 Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    due_date: date = Field(..., description="截止日期")
    estimated_hours: int = Field(default=0, ge=0, description="预估工时")


class TaskCreate(TaskBase):
    """创建任务请求"""
    goal_id: int = Field(..., gt=0, description="目标ID")
    plan_id: Optional[int] = Field(None, gt=0, description="规划ID")


class TaskUpdate(BaseModel):
    """更新任务请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """任务响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    plan_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    due_date: date
    completed: bool
    stage_name: Optional[str] = None
    estimated_hours: int
    task_order: int
    created_at: datetime


class TaskListResponse(BaseModel):
    """任务列表响应（带分页和统计）"""
    total: int = Field(default=0, description="总数")
    completed: int = Field(default=0, description="已完成数")
    data: list = Field(default_factory=list, description="任务列表")
