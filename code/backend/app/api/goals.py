"""
目标 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse, GoalDetailResponse
from app.services.goal_service import goal_service

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("")
async def get_goals(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的目标列表
    """
    try:
        goals = goal_service.get_user_goals(db, current_user.id, status=status)

        # 转换为响应格式
        data = [GoalResponse.model_validate(g).model_dump() for g in goals]

        return success_response(data=data).model_dump()
    except Exception as e:
        return error_response(code=ErrorCode.COMMON_ERROR, message=f"获取目标列表失败: {str(e)}").model_dump()


@router.post("")
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建目标
    """
    try:
        goal = goal_service.create_goal(
            db,
            current_user.id,
            goal_data.title,
            goal_data.description,
            goal_data.deadline
        )

        db.commit()
        db.refresh(goal)

        data = GoalResponse.model_validate(goal)
        return success_response(message="创建成功", data=data.model_dump()).model_dump()

    except ValueError as e:
        return error_response(code=ErrorCode.GOAL_TITLE_EMPTY, message=str(e)).model_dump()
    except Exception as e:
        return error_response(code=ErrorCode.COMMON_ERROR, message=f"创建目标失败: {str(e)}").model_dump()


@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取目标统计信息
    """
    try:
        stats = goal_service.get_goal_statistics(db, current_user.id)
        return success_response(data=stats).model_dump()
    except Exception as e:
        return error_response(code=ErrorCode.COMMON_ERROR, message=f"获取统计信息失败: {str(e)}").model_dump()


@router.get("/{goal_id}")
async def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取目标详情
    """
    try:
        detail = goal_service.get_goal_detail(db, goal_id, current_user.id)

        # 移除 SQLAlchemy 内部属性
        detail.pop("_sa_instance_state", None)

        # 获取关联的规划ID（最新的一个）
        from app.models.plan import Plan
        plan = db.query(Plan).filter(
            Plan.goal_id == goal_id
        ).order_by(Plan.created_at.desc()).first()

        detail["planId"] = plan.id if plan else None

        return success_response(data=detail).model_dump()

    except ValueError as e:
        if str(e) == ERROR_MESSAGES[ErrorCode.GOAL_NOT_FOUND]:
            return error_response(code=ErrorCode.GOAL_NOT_FOUND, message=str(e)).model_dump()
        if str(e) == ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER]:
            return error_response(code=ErrorCode.GOAL_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(code=ErrorCode.COMMON_ERROR, message=f"获取目标详情失败: {str(e)}").model_dump()


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除目标
    """
    try:
        goal_service.delete_goal(db, goal_id, current_user.id)
        return success_response(message="删除成功").model_dump()

    except ValueError as e:
        if str(e) == ERROR_MESSAGES[ErrorCode.GOAL_NOT_FOUND]:
            return error_response(code=ErrorCode.GOAL_NOT_FOUND, message=str(e)).model_dump()
        if str(e) == ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER]:
            return error_response(code=ErrorCode.GOAL_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(code=ErrorCode.COMMON_ERROR, message=f"删除目标失败: {str(e)}").model_dump()
