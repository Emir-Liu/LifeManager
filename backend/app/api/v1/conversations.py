"""
Conversation API
对话相关 API 端点
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.conversation import (
    ActionCreate,
    ActionResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)
from app.services.conversation_service import ConversationService

router = APIRouter()


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建对话会话"""
    service = ConversationService(db)
    conversation = await service.create_conversation(current_user.id, data)
    return conversation


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话会话列表"""
    service = ConversationService(db)
    conversations = await service.get_user_conversations(current_user.id, skip, limit)
    return ConversationListResponse(total=len(conversations), items=conversations)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话会话详情"""
    service = ConversationService(db)
    conversation = await service.get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新对话会话"""
    service = ConversationService(db)
    conversation = await service.update_conversation(conversation_id, current_user.id, data)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除对话会话"""
    service = ConversationService(db)
    success = await service.delete_conversation(conversation_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息"""
    service = ConversationService(db)
    message = await service.add_message(conversation_id, current_user.id, data)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return message


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def list_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话消息列表"""
    service = ConversationService(db)
    messages = await service.get_conversation_messages(
        conversation_id, current_user.id, skip, limit
    )
    return MessageListResponse(total=len(messages), items=messages)


@router.post(
    "/{conversation_id}/actions",
    response_model=ActionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_action(
    conversation_id: int,
    data: ActionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建操作记录"""
    service = ConversationService(db)
    # 获取最后一条消息
    messages = await service.get_conversation_messages(conversation_id, current_user.id, 0, 1)
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages found in conversation",
        )

    action = await service.create_action(
        message_id=messages[0].id,
        conversation_id=conversation_id,
        action_type=data.action_type,
        description=data.description,
        action_data=data.action_data,
    )
    return action
