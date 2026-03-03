"""
Conversation API
对话相关 API 端点 - 同步版本
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.response import success_response, error_response
from app.models.conversation import ConversationAction
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
from app.services.conversation_service_sync import ConversationServiceSync
from app.utils.model_utils import (
    action_to_dict,
    conversation_to_dict,
    message_to_dict,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


# AI 对话请求模型
class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")


class ChatResponse(BaseModel):
    """聊天响应"""
    user_message: MessageResponse
    ai_message: MessageResponse
    actions: List[ActionResponse] = Field(default_factory=list)


@router.post("")
def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建对话会话"""
    try:
        service = ConversationServiceSync(db)
        conversation = service.create_conversation(current_user.id, data)
        return success_response(data=conversation_to_dict(conversation))
    except Exception as e:
        return error_response(code=500, message=f"创建对话失败: {str(e)}")


@router.get("")
def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取对话会话列表"""
    try:
        service = ConversationServiceSync(db)
        conversations = service.get_user_conversations(current_user.id, skip, limit)
        items = [conversation_to_dict(c) for c in conversations]
        return success_response(data={"total": len(conversations), "items": items})
    except Exception as e:
        return error_response(code=500, message=f"获取对话列表失败: {str(e)}")


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取对话会话详情"""
    try:
        service = ConversationServiceSync(db)
        conversation = service.get_conversation(conversation_id, current_user.id)
        if not conversation:
            return error_response(code=404, message="Conversation not found")
        return success_response(data=conversation_to_dict(conversation))
    except Exception as e:
        return error_response(code=500, message=f"获取对话详情失败: {str(e)}")


@router.put("/{conversation_id}")
def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新对话会话"""
    try:
        service = ConversationServiceSync(db)
        conversation = service.update_conversation(conversation_id, current_user.id, data)
        if not conversation:
            return error_response(code=404, message="Conversation not found")
        return success_response(data=conversation_to_dict(conversation))
    except Exception as e:
        return error_response(code=500, message=f"更新对话失败: {str(e)}")


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除对话会话"""
    try:
        service = ConversationServiceSync(db)
        success = service.delete_conversation(conversation_id, current_user.id)
        if not success:
            return error_response(code=404, message="Conversation not found")
        return success_response(message="删除成功")
    except Exception as e:
        return error_response(code=500, message=f"删除对话失败: {str(e)}")


@router.post("/{conversation_id}/messages")
def send_message(
    conversation_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发送消息"""
    try:
        service = ConversationServiceSync(db)
        message = service.add_message(conversation_id, current_user.id, data)
        if not message:
            return error_response(code=404, message="Conversation not found")
        return success_response(data=message_to_dict(message))
    except Exception as e:
        return error_response(code=500, message=f"发送消息失败: {str(e)}")


@router.get("/{conversation_id}/messages")
def list_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取对话消息列表"""
    try:
        service = ConversationServiceSync(db)
        messages = service.get_conversation_messages(
            conversation_id, current_user.id, skip, limit
        )
        items = [message_to_dict(m) for m in messages]
        return success_response(data={"total": len(messages), "items": items})
    except Exception as e:
        return error_response(code=500, message=f"获取消息列表失败: {str(e)}")


@router.post("/{conversation_id}/actions")
def create_action(
    conversation_id: int,
    data: ActionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建操作记录"""
    try:
        service = ConversationServiceSync(db)
        # 获取最后一条消息
        messages = service.get_conversation_messages(conversation_id, current_user.id, 0, 1)
        if not messages:
            return error_response(code=400, message="No messages found in conversation")

        action = service.create_action(
            message_id=messages[0].id,
            conversation_id=conversation_id,
            action_type=data.action_type,
            description=data.description,
            action_data=data.action_data,
        )
        return success_response(data=action_to_dict(action))
    except Exception as e:
        return error_response(code=500, message=f"创建操作记录失败: {str(e)}")


@router.post("/{conversation_id}/chat")
def chat(
    conversation_id: int,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 对话 - 发送消息并获取 AI 回复"""
    # 由于AI服务需要异步，这里暂时返回错误
    return error_response(code=501, message="AI chat功能暂未实现（需要异步支持）")
