"""
任务 API
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
async def get_tasks(
    goal_id: Optional[int] = None,
    date_filter: Optional[date] = None,
    status_filter: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的任务列表
    """
    try:
        tasks = task_service.get_user_tasks(
            db,
            current_user.id,
            goal_id=goal_id,
            date=date_filter,
            status=status_filter
        )

        data = [TaskResponse.model_validate(t).model_dump() for t in tasks]

        return success_response(data=data).model_dump()

    except Exception as e:
        return error_response(message=f"获取任务列表失败: {str(e)}").model_dump()


@router.get("/today")
async def get_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取今日任务
    """
    try:
        result = task_service.get_today_tasks(db, current_user.id)

        tasks_data = [TaskResponse.model_validate(t).model_dump() for t in result["data"]]

        return success_response(data=tasks_data).model_dump()

    except Exception as e:
        return error_response(message=f"获取今日任务失败: {str(e)}").model_dump()


@router.post("")
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建任务
    """
    try:
        task = task_service.create_task(
            db,
            task_data.goal_id,
            current_user.id,
            task_data.title,
            task_data.due_date,
            task_data.description,
            task_data.plan_id,
            task_data.estimated_hours
        )

        data = TaskResponse.model_validate(task)
        return success_response(message="创建成功", data=data.model_dump()).model_dump()

    except ValueError as e:
        if ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER] in str(e):
            return error_response(code=ErrorCode.GOAL_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"创建任务失败: {str(e)}").model_dump()


@router.put("/{task_id}/complete")
async def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    完成任务
    """
    try:
        task = task_service.complete_task(db, task_id, current_user.id)

        data = {
            "id": task.id,
            "completed": task.completed
        }

        return success_response(message="任务已完成", data=data).model_dump()

    except ValueError as e:
        if ERROR_MESSAGES[ErrorCode.TASK_NOT_FOUND] in str(e):
            return error_response(code=ErrorCode.TASK_NOT_FOUND, message=str(e)).model_dump()
        if ERROR_MESSAGES[ErrorCode.TASK_NOT_BELONG_TO_USER] in str(e):
            return error_response(code=ErrorCode.TASK_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"完成任务失败: {str(e)}").model_dump()


@router.put("/{task_id}/uncomplete")
async def uncomplete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    取消完成任务
    """
    try:
        task = task_service.uncomplete_task(db, task_id, current_user.id)

        data = {
            "id": task.id,
            "completed": task.completed
        }

        return success_response(message="已取消完成状态", data=data).model_dump()

    except ValueError as e:
        if ERROR_MESSAGES[ErrorCode.TASK_NOT_FOUND] in str(e):
            return error_response(code=ErrorCode.TASK_NOT_FOUND, message=str(e)).model_dump()
        if ERROR_MESSAGES[ErrorCode.TASK_NOT_BELONG_TO_USER] in str(e):
            return error_response(code=ErrorCode.TASK_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"取消完成任务失败: {str(e)}").model_dump()


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除任务
    """
    try:
        task_service.delete_task(db, task_id, current_user.id)
        return success_response(message="删除成功").model_dump()

    except ValueError as e:
        if ERROR_MESSAGES[ErrorCode.TASK_NOT_FOUND] in str(e):
            return error_response(code=ErrorCode.TASK_NOT_FOUND, message=str(e)).model_dump()
        if ERROR_MESSAGES[ErrorCode.TASK_NOT_BELONG_TO_USER] in str(e):
            return error_response(code=ErrorCode.TASK_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"删除任务失败: {str(e)}").model_dump()
