"""
规划相关的 Pydantic Schema
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class StageTask(BaseModel):
    """阶段任务 Schema"""
    title: str = Field(..., description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    estimated_hours: float = Field(..., ge=0, description="预估工时")
    order: int = Field(..., ge=0, description="任务顺序")


class Stage(BaseModel):
    """阶段 Schema"""
    name: str = Field(..., description="阶段名称")
    order: int = Field(..., ge=0, description="阶段顺序")
    description: Optional[str] = Field(None, description="阶段描述")
    tasks: List[StageTask] = Field(default_factory=list, description="任务列表")


class PlanContent(BaseModel):
    """规划内容 Schema"""
    stages: List[Stage] = Field(..., min_length=2, max_length=6, description="阶段列表")


class PlanGenerateRequest(BaseModel):
    """生成规划请求"""
    goal_id: int = Field(..., gt=0, description="目标ID")
    available_hours_per_day: float = Field(default=2.0, gt=0, le=24, description="每天可用小时数")


class PlanCreate(BaseModel):
    """创建规划请求"""
    goal_id: int = Field(..., gt=0)
    content: Dict[str, Any] = Field(..., description="规划内容(JSON)")


class PlanUpdate(BaseModel):
    """更新规划请求"""
    content: Dict[str, Any] = Field(..., description="规划内容(JSON)")


class PlanResponse(BaseModel):
    """规划响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    content: Dict[str, Any]
    status: str
    total_stages: int
    total_tasks: int
    estimated_total_hours: float
    created_at: datetime
    updated_at: Optional[datetime] = None


class PlanDetailResponse(PlanResponse):
    """规划详情响应（包含目标信息）"""
    goal_title: Optional[str] = None
