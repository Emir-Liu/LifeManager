"""
Event Service (Sync Version)
日程管理服务 - 同步版本
"""
from datetime import datetime, date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate


class EventServiceSync:
    """日程管理服务 - 同步版本"""

    def __init__(self, db: Session):
        self.db = db

    def create_event(self, user_id: int, data: EventCreate) -> Event:
        """创建日程"""
        event = Event(
            user_id=user_id,
            title=data.title,
            description=data.description,
            event_type=data.event_type.value if hasattr(data.event_type, 'value') else data.event_type,
            start_date=data.start_date,
            end_date=data.end_date,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=data.duration_minutes,
            recurrence_rules=data.recurrence_rules,
            color=data.color,
            is_active=data.is_active,
            is_completed=False,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_event(self, event_id: int, user_id: int) -> Optional[Event]:
        """获取日程详情"""
        result = self.db.execute(
            select(Event).where(Event.id == event_id, Event.user_id == user_id)
        )
        return result.scalar_one_or_none()

    def get_user_events(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        event_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Event], int]:
        """获取用户日程列表"""
        query = select(Event).where(Event.user_id == user_id, Event.is_active == True)

        # 过滤条件
        if start_date:
            query = query.where(Event.start_date >= start_date)
        if end_date:
            query = query.where(Event.start_date <= end_date)
        if event_type:
            query = query.where(Event.event_type == event_type)

        # 排序
        query = query.order_by(Event.start_date, Event.start_time)

        # 分页
        result = self.db.execute(query.offset(skip).limit(limit))
        events = list(result.scalars().all())

        # 获取总数
        count_result = self.db.execute(
            select(Event).where(Event.user_id == user_id, Event.is_active == True)
        )
        total = len(count_result.scalars().all())

        return events, total

    def update_event(self, event_id: int, user_id: int, data: EventUpdate) -> Optional[Event]:
        """更新日程"""
        event = self.get_event(event_id, user_id)
        if not event:
            return None

        # 更新字段
        if data.title is not None:
            event.title = data.title
        if data.description is not None:
            event.description = data.description
        if data.event_type is not None:
            event.event_type = data.event_type.value if hasattr(data.event_type, 'value') else data.event_type
        if data.start_date is not None:
            event.start_date = data.start_date
        if data.end_date is not None:
            event.end_date = data.end_date
        if data.start_time is not None:
            event.start_time = data.start_time
        if data.end_time is not None:
            event.end_time = data.end_time
        if data.duration_minutes is not None:
            event.duration_minutes = data.duration_minutes
        if data.recurrence_rules is not None:
            event.recurrence_rules = data.recurrence_rules
        if data.color is not None:
            event.color = data.color
        if data.is_active is not None:
            event.is_active = data.is_active
        if data.is_completed is not None:
            event.is_completed = data.is_completed

        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: int, user_id: int) -> bool:
        """删除日程"""
        event = self.get_event(event_id, user_id)
        if not event:
            return False

        self.db.delete(event)
        self.db.commit()
        return True
