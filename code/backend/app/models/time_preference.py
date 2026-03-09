"""TimePreference Models
时间偏好相关模型
"""
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class TimePreference(Base):
    """用户时间偏好模型"""

    __tablename__ = "time_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # 作息类型
    sleep_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="normal", comment="作息类型"
    )

    # 作息时间
    wake_up_time: Mapped[datetime] = mapped_column(
        Time, nullable=False, default=time(7, 0), comment="起床时间"
    )
    sleep_time: Mapped[datetime] = mapped_column(
        Time, nullable=False, default=time(23, 0), comment="睡眠时间"
    )
    lunch_start: Mapped[datetime] = mapped_column(
        Time, nullable=False, default=time(12, 0), comment="午餐开始"
    )
    lunch_end: Mapped[datetime] = mapped_column(
        Time, nullable=False, default=time(13, 30), comment="午餐结束"
    )

    # 工作时间段
    work_start: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True, comment="工作开始时间")
    work_end: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True, comment="工作结束时间")

    # 工作日（0-6，0=周一）
    work_days: Mapped[Optional[str]] = mapped_column(
        String(7), nullable=True, default="0,1,2,3,4", comment="工作日"
    )

    # 学习时间段
    study_start: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True, comment="学习开始时间")
    study_end: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True, comment="学习结束时间")

    # 首选任务时间段
    preferred_task_start: Mapped[Optional[datetime]] = mapped_column(
        Time, nullable=True, comment="首选任务开始时间"
    )
    preferred_task_end: Mapped[Optional[datetime]] = mapped_column(
        Time, nullable=True, comment="首选任务结束时间"
    )

    # 缓冲时间（分钟）
    buffer_time_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=10, comment="缓冲时间"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="time_preferences")

    def __repr__(self) -> str:
        return f"<TimePreference(id={self.id}, user_id={self.user_id})>"
