"""
Conversation API
对话相关 API 端点 - 同步版本
"""
from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.response import success_response, error_response
from app.core.logger import logger
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
from app.services.chat_service import chat_service
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
    try:
        service = ConversationServiceSync(db)

        # 1. 保存用户消息
        user_message_data = MessageCreate(
            role="user",
            message_type="text",
            content=data.message
        )
        user_message = service.add_message(conversation_id, current_user.id, user_message_data)

        if not user_message:
            return error_response(code=404, message="Conversation not found")

        # 2. 获取对话历史
        messages = service.get_conversation_messages(conversation_id, current_user.id, 0, 10)

        # 3. 调用 AI 获取回复
        history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages[:-1]  # 排除刚刚添加的用户消息
        ]

        ai_response = chat_service.chat(data.message, history)

        # 4. 保存 AI 回复
        ai_message_data = MessageCreate(
            role="assistant",
            message_type="text",
            content=ai_response
        )
        ai_message = service.add_message(conversation_id, current_user.id, ai_message_data)

        if not ai_message:
            logger.warning(f"保存 AI 回复失败，但已返回给用户")

        return success_response(data={
            "user_message": message_to_dict(user_message),
            "ai_message": message_to_dict(ai_message) if ai_message else None
        })

    except Exception as e:
        logger.error(f"AI chat 错误: {e}", exc_info=True)
        return error_response(code=500, message=f"AI 对话失败: {str(e)}")


@router.post("/{conversation_id}/chat/stream")
async def chat_stream(
    conversation_id: int,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """流式 AI 对话 - 发送消息并流式获取 AI 回复"""
    try:
        service = ConversationServiceSync(db)

        # 1. 保存用户消息
        user_message_data = MessageCreate(
            role="user",
            message_type="text",
            content=data.message
        )
        user_message = service.add_message(conversation_id, current_user.id, user_message_data)

        if not user_message:
            return error_response(code=404, message="Conversation not found")

        # 2. 获取对话历史
        messages = service.get_conversation_messages(conversation_id, current_user.id, 0, 10)
        history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages[:-1]  # 排除刚刚添加的用户消息
        ]

        # 3. 生成流式响应
        async def generate_stream():
            try:
                # 先返回用户消息
                yield f"event: user_message\ndata: {json.dumps(message_to_dict(user_message))}\n\n"

                # 流式输出 AI 回复
                ai_response = ""
                async for chunk in chat_service.chat_stream(data.message, history):
                    ai_response += chunk
                    yield f"event: ai_chunk\ndata: {json.dumps({'content': chunk})}\n\n"

                # 保存 AI 回复
                ai_message_data = MessageCreate(
                    role="assistant",
                    message_type="text",
                    content=ai_response
                )
                ai_message = service.add_message(conversation_id, current_user.id, ai_message_data)

                # 返回完整消息
                yield f"event: ai_complete\ndata: {json.dumps(message_to_dict(ai_message))}\n\n"

            except Exception as e:
                logger.error(f"流式输出错误: {e}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"AI chat stream 错误: {e}", exc_info=True)
        return error_response(code=500, message=f"AI 对话失败: {str(e)}")
