"""
Timeline API
时间线相关 API 端点
"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.response import success_response, error_response
from app.models.user import User
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/timeline", tags=["timeline"])


# Schema定义
class TimeAssignRequest(BaseModel):
    """时间分配请求"""
    task_id: int = Field(..., description="任务ID")
    due_date: datetime = Field(..., description="截止日期")
    duration_minutes: int = Field(..., gt=0, description="持续时间(分钟)")


class AutoAssignRequest(BaseModel):
    """自动分配请求"""
    task_id: int = Field(..., description="任务ID")
    due_date: datetime = Field(..., description="截止日期")
    duration_minutes: int = Field(..., gt=0, description="持续时间(分钟)")


@router.post("/suggest")
async def suggest_task_time(
    data: TimeAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """建议任务时间"""
    try:
        service = ScheduleService(db)
        suggestion = await service.suggest_task_time(
            task_id=data.task_id,
            due_date=data.due_date,
            duration_minutes=data.duration_minutes,
            user_id=current_user.id,
        )
        return success_response(data=suggestion.model_dump())
    except Exception as e:
        return error_response(code=500, message=f"建议任务时间失败: {str(e)}")


@router.post("/auto-assign")
async def auto_assign_task(
    data: AutoAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """自动分配任务时间"""
    try:
        service = ScheduleService(db)
        result = await service.auto_assign_task(
            task_id=data.task_id,
            due_date=data.due_date,
            duration_minutes=data.duration_minutes,
            user_id=current_user.id,
        )
        return success_response(data=result.model_dump())
    except Exception as e:
        return error_response(code=500, message=f"自动分配任务失败: {str(e)}")


@router.get("/{date_str}")
async def get_timeline(
    date_str: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取指定日期的时间线

    Args:
        date_str: 日期字符串,格式: YYYY-MM-DD
    """
    try:
        due_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return error_response(code=400, message="Invalid date format. Use YYYY-MM-DD")

    try:
        service = ScheduleService(db)
        timeline = await service.get_timeline(due_date, current_user.id)
        return success_response(data=timeline.model_dump())
    except Exception as e:
        return error_response(code=500, message=f"获取时间线失败: {str(e)}")
