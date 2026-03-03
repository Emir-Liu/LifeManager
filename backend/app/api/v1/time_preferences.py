"""
TimePreference API
时间偏好相关 API 端点 - 同步版本
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.response import success_response, error_response
from app.models.user import User
from app.schemas.time_preference import (
    TimePreferenceCreate,
    TimePreferenceResponse,
    TimeStatsResponse,
    TimePreferenceUpdate,
)
from app.services.time_preference_service_sync import TimePreferenceServiceSync
from app.utils.model_utils import time_preference_to_dict

router = APIRouter(prefix="/time-preferences", tags=["time-preferences"])


@router.post("")
def create_time_preference(
    data: TimePreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建时间偏好"""
    try:
        service = TimePreferenceServiceSync(db)
        preference = service.create_time_preference(current_user.id, data)
        return success_response(data=time_preference_to_dict(preference))
    except Exception as e:
        return error_response(code=500, message=f"创建时间偏好失败: {str(e)}")


@router.get("")
def get_time_preference(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户时间偏好"""
    try:
        service = TimePreferenceServiceSync(db)
        preference = service.get_user_time_preference(current_user.id)
        if not preference:
            return error_response(code=404, message="Time preference not found")
        return success_response(data=time_preference_to_dict(preference))
    except Exception as e:
        return error_response(code=500, message=f"获取时间偏好失败: {str(e)}")


@router.put("")
def update_time_preference(
    data: TimePreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新时间偏好"""
    try:
        service = TimePreferenceServiceSync(db)
        preference = service.update_time_preference(current_user.id, data)
        if not preference:
            return error_response(code=404, message="Time preference not found")
        return success_response(data=time_preference_to_dict(preference))
    except Exception as e:
        return error_response(code=500, message=f"更新时间偏好失败: {str(e)}")


@router.get("/stats")
def get_time_stats(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取时间统计"""
    try:
        service = TimePreferenceServiceSync(db)
        stats = service.get_time_stats(
            current_user.id,
            start_date=start_date,
            end_date=end_date,
        )
        return success_response(data=stats.model_dump())
    except Exception as e:
        return error_response(code=500, message=f"获取时间统计失败: {str(e)}")
