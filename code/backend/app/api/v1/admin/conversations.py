"""Admin Conversation API
管理员对话管理 API 端点
"""
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.response import success_response, error_response
from app.core.logger import logger
from app.models.user import User
from app.models.conversation import Conversation, ConversationMessage
from app.utils.model_utils import (
    conversation_to_dict,
    message_to_dict,
)

router = APIRouter(prefix="/admin/conversations", tags=["admin-conversations"])


# 临时管理员用户ID列表（后续应该完善用户角色系统）
ADMIN_USER_IDS = [1]  # 允许用户ID为1的用户访问管理功能


def check_admin_permission(current_user: User):
    """检查管理员权限"""
    if current_user.id not in ADMIN_USER_IDS:
        raise HTTPException(
            status_code=403,
            detail="需要管理员权限"
        )
    return current_user


@router.get("")
def list_all_conversations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    conversation_type: Optional[str] = Query(None, description="按对话类型筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    search: Optional[str] = Query(None, description="搜索对话标题"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员获取所有对话列表"""
    try:
        # 检查管理员权限
        check_admin_permission(current_user)

        # 构建查询
        query = db.query(Conversation)

        # 添加筛选条件
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        if conversation_type:
            query = query.filter(Conversation.conversation_type == conversation_type)
        if status:
            query = query.filter(Conversation.status == status)
        if search:
            query = query.filter(Conversation.title.contains(search))
        if start_date:
            query = query.filter(Conversation.created_at >= start_date)
        if end_date:
            query = query.filter(Conversation.created_at <= end_date)

        # 排序和分页
        total = query.count()
        conversations = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()

        items = [conversation_to_dict(conv) for conv in conversations]

        return success_response(data={
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员获取对话列表失败: {e}", exc_info=True)
        return error_response(code=500, message=f"获取对话列表失败: {str(e)}")


@router.get("/{conversation_id}")
def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员获取对话详情"""
    try:
        # 检查管理员权限
        check_admin_permission(current_user)

        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return error_response(code=404, message="对话不存在")

        return success_response(data=conversation_to_dict(conversation))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员获取对话详情失败: {e}", exc_info=True)
        return error_response(code=500, message=f"获取对话详情失败: {str(e)}")


@router.get("/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="每页记录数"),
    role: Optional[str] = Query(None, description="按角色筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员获取对话消息列表"""
    try:
        # 检查管理员权限
        check_admin_permission(current_user)

        # 构建查询
        query = db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        )

        # 添加筛选条件
        if role:
            query = query.filter(ConversationMessage.role == role)

        # 排序和分页
        total = query.count()
        messages = query.order_by(ConversationMessage.sequence.asc()).offset(skip).limit(limit).all()

        items = [message_to_dict(msg) for msg in messages]

        return success_response(data={
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员获取消息列表失败: {e}", exc_info=True)
        return error_response(code=500, message=f"获取消息列表失败: {str(e)}")


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员删除对话"""
    try:
        # 检查管理员权限
        check_admin_permission(current_user)

        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return error_response(code=404, message="对话不存在")

        # 删除对话（级联删除消息和操作）
        db.delete(conversation)
        db.commit()

        logger.info(f"管理员 {current_user.id} 删除了对话 {conversation_id}")

        return success_response(message="删除成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员删除对话失败: {e}", exc_info=True)
        return error_response(code=500, message=f"删除对话失败: {str(e)}")


@router.get("/users/{user_id}/conversations")
def get_user_conversations(
    user_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员获取用户的所有对话"""
    try:
        # 检查管理员权限
        check_admin_permission(current_user)

        query = db.query(Conversation).filter(Conversation.user_id == user_id)

        total = query.count()
        conversations = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()

        items = [conversation_to_dict(conv) for conv in conversations]

        return success_response(data={
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员获取用户对话失败: {e}", exc_info=True)
        return error_response(code=500, message=f"获取用户对话失败: {str(e)}")


@router.get("/messages/search")
def search_messages(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员搜索消息内容"""
    try:
        # 检查管理员权限
        check_admin_permission(current_user)

        # 构建查询
        query = db.query(ConversationMessage).filter(
            ConversationMessage.content.contains(keyword)
        )

        # 添加用户筛选
        if user_id:
            query = query.join(Conversation).filter(Conversation.user_id == user_id)

        # 排序和分页
        total = query.count()
        messages = query.order_by(ConversationMessage.created_at.desc()).offset(skip).limit(limit).all()

        items = [message_to_dict(msg) for msg in messages]

        return success_response(data={
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit,
            "keyword": keyword
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员搜索消息失败: {e}", exc_info=True)
        return error_response(code=500, message=f"搜索消息失败: {str(e)}")


class ConversationStatsResponse(BaseModel):
    """对话统计响应"""
    total_conversations: int = Field(..., description="总对话数")
    total_messages: int = Field(..., description="总消息数")
    total_users: int = Field(..., description="总用户数")
    active_conversations: int = Field(..., description="活跃对话数")
    conversations_by_type: dict = Field(default_factory=dict, description="按类型分组的对话数")
    conversations_by_status: dict = Field(default_factory=dict, description="按状态分组的对话数")


@router.get("/stats/overview", response_model=ConversationStatsResponse)
def get_conversation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """管理员获取对话统计信息"""
    try:
        # 检查管理员权限
        check_admin_permission(current_user)

        # 总对话数
        total_conversations = db.query(Conversation).count()

        # 总消息数
        total_messages = db.query(ConversationMessage).count()

        # 总用户数（有对话的用户）
        from sqlalchemy import func
        total_users = db.query(func.count(func.distinct(Conversation.user_id))).scalar()

        # 活跃对话数
        active_conversations = db.query(Conversation).filter(
            Conversation.status == "active"
        ).count()

        # 按类型分组
        conversations_by_type = {}
        type_results = db.query(
            Conversation.conversation_type,
            func.count(Conversation.id)
        ).group_by(Conversation.conversation_type).all()
        for conv_type, count in type_results:
            conversations_by_type[conv_type] = count

        # 按状态分组
        conversations_by_status = {}
        status_results = db.query(
            Conversation.status,
            func.count(Conversation.id)
        ).group_by(Conversation.status).all()
        for status, count in status_results:
            conversations_by_status[status] = count

        return success_response(data={
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_users": total_users,
            "active_conversations": active_conversations,
            "conversations_by_type": conversations_by_type,
            "conversations_by_status": conversations_by_status
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员获取对话统计失败: {e}", exc_info=True)
        return error_response(code=500, message=f"获取对话统计失败: {str(e)}")
