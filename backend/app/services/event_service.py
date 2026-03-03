"""
Event Service
日程管理服务
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate


class EventService:
    """日程管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event(self, user_id: int, data: EventCreate) -> Event:
        """创建日程"""
        event = Event(
            user_id=user_id,
            title=data.title,
            description=data.description,
            event_type=data.event_type.value,
            start_date=data.start_date,
            end_date=data.end_date,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=data.duration_minutes,
            recurrence_rules=data.recurrence_rules,
            color=data.color,
            is_active=data.is_active,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_event(self, event_id: int, user_id: int) -> Optional[Event]:
        """获取日程详情"""
        result = await self.db.execute(
            select(Event).where(Event.id == event_id, Event.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_events(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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
        result = await self.db.execute(query.offset(skip).limit(limit))
        events = list(result.scalars().all())

        # 获取总数
        count_result = await self.db.execute(
            select(Event).where(Event.user_id == user_id, Event.is_active == True)
        )
        total = len(count_result.scalars().all())

        return events, total

    async def update_event(
        self, event_id: int, user_id: int, data: EventUpdate
    ) -> Optional[Event]:
        """更新日程"""
        # 构建更新数据
        update_data = {}
        if data.title is not None:
            update_data["title"] = data.title
        if data.description is not None:
            update_data["description"] = data.description
        if data.event_type is not None:
            update_data["event_type"] = data.event_type.value
        if data.start_date is not None:
            update_data["start_date"] = data.start_date
        if data.end_date is not None:
            update_data["end_date"] = data.end_date
        if data.start_time is not None:
            update_data["start_time"] = data.start_time
        if data.end_time is not None:
            update_data["end_time"] = data.end_time
        if data.duration_minutes is not None:
            update_data["duration_minutes"] = data.duration_minutes
        if data.recurrence_rules is not None:
            update_data["recurrence_rules"] = data.recurrence_rules
        if data.color is not None:
            update_data["color"] = data.color
        if data.is_active is not None:
            update_data["is_active"] = data.is_active

        if not update_data:
            return await self.get_event(event_id, user_id)

        # 执行更新
        await self.db.execute(
            update(Event)
            .where(Event.id == event_id, Event.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()

        return await self.get_event(event_id, user_id)

    async def delete_event(self, event_id: int, user_id: int) -> bool:
        """删除日程"""
        result = await self.db.execute(
            delete(Event).where(Event.id == event_id, Event.user_id == user_id)
        )
        await self.db.commit()
        return result.rowcount > 0
