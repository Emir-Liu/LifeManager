"""
Conversation Service
对话服务层 - 负责对话会话、消息、操作管理
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.conversation import (
    Action,
    ActionStatus,
    Conversation,
    ConversationAction,
    ConversationMessage,
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


class ConversationService:
    """对话服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversation(
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
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> Optional[Conversation]:
        """获取对话会话"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(
                selectinload(Conversation.messages).selectinload(
                    ConversationMessage.actions
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_conversations(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Conversation]:
        """获取用户的对话会话列表"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_conversation(
        self, conversation_id: int, user_id: int, data: ConversationUpdate
    ) -> Optional[Conversation]:
        """更新对话会话"""
        conversation = await self.get_conversation(conversation_id, user_id)
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

        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """删除对话会话"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.commit()

        return True

    async def add_message(
        self, conversation_id: int, user_id: int, data: MessageCreate
    ) -> Optional[ConversationMessage]:
        """添加消息"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None

        # 获取当前消息序号
        result = await self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.sequence.desc())
            .limit(1)
        )
        last_message = result.scalar_one_or_none()
        next_sequence = (last_message.sequence + 1) if last_message else 1

        message = ConversationMessage(
            conversation_id=conversation_id,
            sequence=next_sequence,
            role=data.role,
            message_type=data.message_type,
            content=data.content,
            content_json=data.content_json,
            model_used=data.model_used,
            tokens_used=data.tokens_used or 0,
        )

        self.db.add(message)

        # 更新会话消息计数
        conversation.message_count += 1

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_conversation_messages(
        self, conversation_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ConversationMessage]:
        """获取对话消息列表"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []

        result = await self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.sequence.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_action(
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
            conversation_id=conversation_id,
            action_type=action_type,
            status=ActionStatus.PENDING,
            description=description,
            action_data=action_data,
        )

        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)

        return action

    async def execute_action(
        self,
        action_id: int,
        target_type: Optional[str],
        target_id: Optional[int],
        result_message: str,
    ) -> Optional[ConversationAction]:
        """执行操作"""
        result = await self.db.execute(select(ConversationAction).where(ConversationAction.id == action_id))
        action = result.scalar_one_or_none()
        if not action:
            return None

        action.status = ActionStatus.EXECUTED
        action.target_type = target_type
        action.target_id = target_id
        action.result_message = result_message

        await self.db.commit()
        await self.db.refresh(action)

        return action
