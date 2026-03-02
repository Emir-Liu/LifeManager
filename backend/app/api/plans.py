"""
规划 API
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.models.user import User
from app.schemas.plan import PlanGenerateRequest, PlanResponse, PlanDetailResponse
from app.services.plan_service import plan_service

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/generate")
async def generate_plan(
    request: PlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成规划（调用 AI）
    """
    try:
        plan = plan_service.generate_plan(
            db,
            current_user.id,
            request.goal_id,
            request.available_hours_per_day
        )

        # 解析 content JSON 字符串为对象
        content_obj = json.loads(plan.content) if plan.content else {"stages": []}
        
        data = {
            "id": plan.id,
            "goal_id": plan.goal_id,
            "content": content_obj,
            "status": plan.status,
            "total_stages": plan.total_stages,
            "total_tasks": plan.total_tasks,
            "estimated_total_hours": plan.estimated_total_hours
        }

        return success_response(message="规划生成成功", data=data).model_dump()

    except ValueError as e:
        error_code = ErrorCode.GOAL_NOT_FOUND
        if ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER] in str(e):
            error_code = ErrorCode.GOAL_NOT_BELONG_TO_USER
        return error_response(code=error_code, message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"生成规划失败: {str(e)}").model_dump()


@router.get("/{plan_id}")
async def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取规划详情
    """
    try:
        plan = plan_service.get_plan_by_id(db, plan_id, current_user.id)

        # 解析 content JSON 字符串为对象
        content_obj = json.loads(plan.content) if plan.content else {"stages": []}

        data = {
            "id": plan.id,
            "goal_id": plan.goal_id,
            "goal_title": plan.goal.title,
            "content": content_obj,
            "status": plan.status,
            "total_stages": plan.total_stages,
            "total_tasks": plan.total_tasks,
            "estimated_total_hours": plan.estimated_total_hours,
            "created_at": plan.created_at.isoformat() if plan.created_at else None
        }

        return success_response(data=data).model_dump()

    except ValueError as e:
        error_code = ErrorCode.PLAN_NOT_FOUND
        if ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER] in str(e):
            error_code = ErrorCode.GOAL_NOT_BELONG_TO_USER
        return error_response(code=error_code, message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"获取规划详情失败: {str(e)}").model_dump()


@router.post("/{plan_id}/confirm")
async def confirm_plan(
    plan_id: int,
    content: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    确认规划（创建所有任务）
    """
    try:
        result = plan_service.confirm_plan(db, plan_id, current_user.id, content)

        return success_response(
            message=f"规划确认成功，已创建 {result['tasks_created']} 个任务",
            data=result
        ).model_dump()

    except ValueError as e:
        if ERROR_MESSAGES[ErrorCode.PLAN_NOT_FOUND] in str(e):
            return error_response(code=ErrorCode.PLAN_NOT_FOUND, message=str(e)).model_dump()
        if ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER] in str(e):
            return error_response(code=ErrorCode.GOAL_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        if ERROR_MESSAGES[ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY] in str(e):
            return error_response(code=ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"确认规划失败: {str(e)}").model_dump()


@router.put("/{plan_id}")
async def update_plan(
    plan_id: int,
    content: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    修改规划
    """
    try:
        plan = plan_service.update_plan(db, plan_id, current_user.id, content)

        # 解析 content JSON 字符串为对象
        content_obj = json.loads(plan.content) if plan.content else {"stages": []}

        data = {
            "id": plan.id,
            "content": content_obj,
            "total_stages": plan.total_stages,
            "total_tasks": plan.total_tasks,
            "estimated_total_hours": plan.estimated_total_hours
        }

        return success_response(message="修改成功", data=data).model_dump()

    except ValueError as e:
        if ERROR_MESSAGES[ErrorCode.PLAN_NOT_FOUND] in str(e):
            return error_response(code=ErrorCode.PLAN_NOT_FOUND, message=str(e)).model_dump()
        if ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER] in str(e):
            return error_response(code=ErrorCode.GOAL_NOT_BELONG_TO_USER, message=str(e)).model_dump()
        if ERROR_MESSAGES[ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY] in str(e):
            return error_response(code=ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY, message=str(e)).model_dump()
        return error_response(message=str(e)).model_dump()
    except Exception as e:
        return error_response(message=f"修改规划失败: {str(e)}").model_dump()
