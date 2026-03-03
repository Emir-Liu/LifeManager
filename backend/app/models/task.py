"""
任务模型 - Phase 2 增强版本
支持时间段任务、周期性任务、任务层级
"""
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.goal import Goal
    from app.models.plan import Plan


class Task(Base):
    """任务模型 - Phase 2 增强版本"""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    goal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True, comment="目标ID"
    )
    plan_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=True, comment="规划ID"
    )

    # 基本信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="任务标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="任务描述")

    # 时间安排（Phase 2 新增）
    due_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True, comment="截止日期")
    start_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True, comment="开始时间")
    end_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True, comment="结束时间")
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="持续时间（分钟）")

    # 实际时间记录
    actual_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="实际开始时间")
    actual_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="实际结束时间")

    # 任务状态
    completed: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否完成")
    stage_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="阶段名称")

    # 工时估算（修改为 Float 类型）
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0, comment="预估工时（小时）")

    # 任务层级（Phase 2 新增）
    parent_task_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, comment="父任务ID"
    )

    # 任务类型（Phase 2 新增）
    task_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="general", comment="任务类型"
    )

    # 提醒设置（Phase 2 新增）
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否开启提醒")
    reminder_minutes_before: Mapped[int] = mapped_column(
        Integer, default=30, comment="提前提醒分钟数"
    )

    # 周期性规则（Phase 2 新增）- 遵循 iCalendar RFC5545 标准
    recurrence_rule: Mapped[Optional[dict]] = mapped_column(
        String(500), nullable=True, comment="周期性规则（RRULE）"
    )
    excluded_dates: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="排除日期列表（逗号分隔，格式：YYYY-MM-DD）"
    )
    additional_dates: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="额外日期列表（逗号分隔，格式：YYYY-MM-DD）"
    )

    # 排序
    task_order: Mapped[int] = mapped_column(Integer, default=0, comment="任务顺序")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), comment="更新时间")

    # 关系
    goal: Mapped["Goal"] = relationship("Goal", back_populates="tasks")
    plan: Mapped[Optional["Plan"]] = relationship("Plan", back_populates="tasks")
    parent_task: Mapped[Optional["Task"]] = relationship("Task", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, completed={self.completed})>"
