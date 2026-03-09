"""Event Models
日程相关模型
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Event(Base):
    """日程模型 - 支持重复规则"""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 基本信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="日程标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="日程描述")
    event_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="general", comment="日程类型"
    )

    # 时间安排
    start_date: Mapped[datetime] = mapped_column(Date, nullable=False, comment="开始日期")
    end_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True, comment="结束日期")
    start_time: Mapped[datetime] = mapped_column(Time, nullable=False, comment="开始时间")
    end_time: Mapped[datetime] = mapped_column(Time, nullable=False, comment="结束时间")
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, comment="持续时间（分钟）")

    # 重复规则（支持多个重复规则）
    recurrence_rules: Mapped[Optional[dict]] = mapped_column(
        String(1000), nullable=True, comment="重复规则数组，每项遵循 iCalendar 标准"
    )

    # 颜色标记
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#666666", comment="十六进制颜色")

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")

    # 父日程（支持日程层级）
    parent_event_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="events")
    parent_event: Mapped[Optional["Event"]] = relationship("Event", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, title={self.title}, type={self.event_type})>"
