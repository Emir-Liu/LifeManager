"""
Model Utils
模型转换工具 - 处理SQLAlchemy model到dict的转换
"""
from datetime import datetime
from typing import Any


def model_to_dict(model: Any, exclude: list[str] = None) -> dict:
    """
    将SQLAlchemy model转换为字典

    Args:
        model: SQLAlchemy model实例
        exclude: 要排除的字段列表

    Returns:
        dict: 转换后的字典
    """
    if exclude is None:
        exclude = []

    result = {}
    for column in model.__table__.columns:
        column_name = column.name
        if column_name not in exclude:
            value = getattr(model, column_name)

            # 处理datetime类型
            if isinstance(value, datetime):
                value = value.isoformat()

            result[column_name] = value

    return result


def model_list_to_dict(models: list[Any], exclude: list[str] = None) -> list[dict]:
    """
    将SQLAlchemy model列表转换为字典列表

    Args:
        models: SQLAlchemy model实例列表
        exclude: 要排除的字段列表

    Returns:
        list[dict]: 转换后的字典列表
    """
    return [model_to_dict(model, exclude) for model in models]


def conversation_to_dict(conversation) -> dict:
    """转换Conversation对象"""
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "conversation_type": conversation.conversation_type,
        "status": conversation.status,
        "related_goal_id": conversation.related_goal_id,
        "related_plan_id": conversation.related_plan_id,
        "context_summary": conversation.context_summary,
        "context_json": conversation.context_json,
        "message_count": conversation.message_count,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
        "completed_at": conversation.completed_at.isoformat() if conversation.completed_at else None,
    }


def message_to_dict(message) -> dict:
    """转换ConversationMessage对象"""
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sequence": message.sequence,
        "role": message.role,
        "message_type": message.message_type,
        "content": message.content,
        "content_json": message.content_json,
        "model_used": message.model_used,
        "tokens_used": message.tokens_used,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


def action_to_dict(action) -> dict:
    """转换ConversationAction对象"""
    return {
        "id": action.id,
        "message_id": action.message_id,
        "conversation_id": action.conversation_id,
        "action_type": action.action_type,
        "description": action.description,
        "action_data": action.action_data,
        "status": action.status,
        "executed_at": action.executed_at.isoformat() if action.executed_at else None,
        "created_at": action.created_at.isoformat() if action.created_at else None,
    }


def event_to_dict(event) -> dict:
    """转换Event对象"""
    return {
        "id": event.id,
        "user_id": event.user_id,
        "title": event.title,
        "event_type": event.event_type,
        "start_time": event.start_time.isoformat() if event.start_time else None,
        "end_time": event.end_time.isoformat() if event.end_time else None,
        "description": event.description,
        "location": event.location,
        "is_completed": event.is_completed,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
    }


def time_preference_to_dict(preference) -> dict:
    """转换TimePreference对象"""
    return {
        "id": preference.id,
        "user_id": preference.user_id,
        "preferred_start_time": preference.preferred_start_time,
        "preferred_end_time": preference.preferred_end_time,
        "break_duration": preference.break_duration,
        "max_continuous_work": preference.max_continuous_work,
        "work_days": preference.work_days,
        "created_at": preference.created_at.isoformat() if preference.created_at else None,
        "updated_at": preference.updated_at.isoformat() if preference.updated_at else None,
    }
