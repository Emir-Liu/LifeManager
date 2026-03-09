"""
Conversation Service (Sync Version)
对话服务层 - 同步版本，用于与现有代码集成
"""
from typing import Optional

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.models.conversation import (
    Conversation,
    ConversationAction,
    ConversationMessage,
)
from app.schemas.conversation import (
    Action,
    ActionStatus,
    ConversationStatus,
    ConversationType,
    MessageRole,
    MessageType,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
)


class ConversationServiceSync:
    """对话服务 - 同步版本"""

    def __init__(self, db: Session):
        self.db = db

    def create_conversation(
        self, user_id: int, data: ConversationCreate
    ) -> Conversation:
        """创建对话会话"""
        conversation = Conversation(
            user_id=user_id,
            title=data.title,
            conversation_type=data.conversation_type,
            status=ConversationStatus.ACTIVE,
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> Optional[Conversation]:
        """获取对话会话"""
        result = self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(
                selectinload(Conversation.messages).selectinload(
                    ConversationMessage.actions
                )
            )
        )
        return result.scalar_one_or_none()

    def get_user_conversations(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Conversation]:
        """获取用户的对话会话列表"""
        result = self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    def update_conversation(
        self, conversation_id: int, user_id: int, data: ConversationUpdate
    ) -> Optional[Conversation]:
        """更新对话会话"""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        if data.title is not None:
            conversation.title = data.title
        if data.status is not None:
            conversation.status = data.status
        if data.context_summary is not None:
            conversation.context_summary = data.context_summary
        if data.context_json is not None:
            conversation.context_json = data.context_json

        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete_conversation(
        self, conversation_id: int, user_id: int
    ) -> bool:
        """删除对话会话"""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()
        return True

    def add_message(
        self, conversation_id: int, user_id: int, data: MessageCreate
    ) -> Optional[ConversationMessage]:
        """添加消息到对话"""
        # 验证对话所有权
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        # 获取最后一条消息的序列号
        last_message = (
            self.db.execute(
                select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conversation_id)
                .order_by(ConversationMessage.sequence.desc())
                .limit(1)
            )
            .scalar_one_or_none()
        )
        sequence = (last_message.sequence + 1) if last_message else 1

        message = ConversationMessage(
            conversation_id=conversation_id,
            sequence=sequence,
            role=data.role,
            message_type=data.message_type,
            content=data.content,
            content_json=data.content_json,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # 更新对话的最后活动时间
        conversation.updated_at = None  # 触发自动更新
        self.db.commit()

        return message

    def get_conversation_messages(
        self,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConversationMessage]:
        """获取对话消息列表"""
        # 验证对话所有权
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        result = self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.sequence.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    def create_action(
        self,
        message_id: int,
        conversation_id: int,
        action_type: Action,
        description: str,
        action_data: Optional[dict] = None,
    ) -> ConversationAction:
        """创建操作记录"""
        action = ConversationAction(
            message_id=message_id,
            action_type=action_type,
            description=description,
            action_data=action_data,
            status=ActionStatus.PENDING,
        )

        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action
