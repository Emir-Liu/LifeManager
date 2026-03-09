"""
Event API
日程相关 API 端点 - 同步版本
"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.response import success_response, error_response
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventListResponse,
    EventResponse,
    EventUpdate,
)
from app.services.event_service_sync import EventServiceSync
from app.utils.model_utils import event_to_dict

router = APIRouter(prefix="/events", tags=["events"])


@router.post("")
def create_event(
    data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建日程"""
    try:
        service = EventServiceSync(db)
        event = service.create_event(current_user.id, data)
        return success_response(data=event_to_dict(event))
    except Exception as e:
        return error_response(code=500, message=f"创建日程失败: {str(e)}")


@router.get("")
def list_events(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    event_type: Optional[str] = Query(None, description="日程类型"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日程列表"""
    try:
        service = EventServiceSync(db)
        events, total = service.get_user_events(
            current_user.id,
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            skip=skip,
            limit=limit,
        )
        items = [event_to_dict(e) for e in events]
        return success_response(data={"total": total, "items": items})
    except Exception as e:
        return error_response(code=500, message=f"获取日程列表失败: {str(e)}")


@router.get("/{event_id}")
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日程详情"""
    try:
        service = EventServiceSync(db)
        event = service.get_event(event_id, current_user.id)
        if not event:
            return error_response(code=404, message="Event not found")
        return success_response(data=event_to_dict(event))
    except Exception as e:
        return error_response(code=500, message=f"获取日程详情失败: {str(e)}")


@router.put("/{event_id}")
def update_event(
    event_id: int,
    data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新日程"""
    try:
        service = EventServiceSync(db)
        event = service.update_event(event_id, current_user.id, data)
        if not event:
            return error_response(code=404, message="Event not found")
        return success_response(data=event_to_dict(event))
    except Exception as e:
        return error_response(code=500, message=f"更新日程失败: {str(e)}")


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除日程"""
    try:
        service = EventServiceSync(db)
        success = service.delete_event(event_id, current_user.id)
        if not success:
            return error_response(code=404, message="Event not found")
        return success_response(message="删除成功")
    except Exception as e:
        return error_response(code=500, message=f"删除日程失败: {str(e)}")
