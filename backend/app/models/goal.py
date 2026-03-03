"""目标模型 - Phase 2 增强版本
支持目标层级、优先级管理
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.plan import Plan
    from app.models.task import Task
    from app.models.user import User
    from app.models.conversation import Conversation


class Goal(Base):
    """目标模型 - Phase 2 增强版本"""

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID"
    )

    # 基本信息
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="目标标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="目标描述")

    # 时间安排
    deadline: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True, index=True, comment="截止日期")

    # 状态管理（Phase 2 增强）
    status: Mapped[str] = mapped_column(
        String(20), default="planning", index=True, comment="状态"
    )

    # 目标层级（Phase 2 新增）
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, comment="父目标ID"
    )

    # 优先级（Phase 2 新增）
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium", comment="优先级"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, onupdate=func.now(), comment="更新时间"
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="goals")
    plans: Mapped[list["Plan"]] = relationship("Plan", back_populates="goal", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="goal", cascade="all, delete-orphan")
    parent_goal: Mapped[Optional["Goal"]] = relationship("Goal", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, title={self.title}, status={self.status})>"
