"""
Conversation Models
对话会话相关模型
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Conversation(Base):
    """对话会话模型"""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 基本信息
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="对话标题")
    conversation_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="goal_planning", comment="对话类型"
    )

    # 状态管理
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", comment="状态"
    )

    # 关联信息
    related_goal_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, comment="关联目标ID"
    )
    related_plan_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True, comment="关联规划ID"
    )

    # 上下文管理
    context_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="对话摘要")
    context_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="完整上下文数据")

    # 统计信息
    message_count: Mapped[int] = mapped_column(Integer, default=0, comment="消息数量")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="完成时间")

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="conversation", cascade="all, delete-orphan"
    )
    actions: Mapped[list["ConversationAction"]] = relationship(
        "ConversationAction", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title={self.title}, type={self.conversation_type})>"


class ConversationMessage(Base):
    """对话消息模型"""

    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 消息序列
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, comment="消息序号")

    # 消息内容
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="角色")
    message_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="text", comment="消息类型"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    content_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="结构化内容数据")

    # AI 模型信息
    model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="使用的AI模型")
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, comment="消耗的token数")

    # 用户反馈
    user_feedback: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="用户反馈"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    actions: Mapped[list["ConversationAction"]] = relationship(
        "ConversationAction", back_populates="message", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ConversationMessage(id={self.id}, role={self.role}, sequence={self.sequence})>"


class ConversationAction(Base):
    """对话操作记录模型"""

    __tablename__ = "conversation_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversation_messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 操作信息
    action_type: Mapped[str] = mapped_column(String(30), nullable=False, comment="操作类型")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", comment="状态"
    )

    # 操作详情
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="操作描述")
    action_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="操作数据")

    # 目标信息
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="目标类型")
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="目标ID")

    # 执行结果
    result_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="执行结果消息")
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="执行时间")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关系
    message: Mapped["ConversationMessage"] = relationship("ConversationMessage", back_populates="actions")
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="actions")

    def __repr__(self) -> str:
        return f"<ConversationAction(id={self.id}, type={self.action_type}, status={self.status})>"
