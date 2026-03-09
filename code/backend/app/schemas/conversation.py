"""
Conversation Schemas
对话相关的 Pydantic Schema
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# 枚举定义
class ConversationStatus(str, Enum):
    """对话状态"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConversationType(str, Enum):
    """对话类型"""
    GOAL_PLANNING = "goal_planning"
    SCHEDULE_PLANNING = "schedule_planning"
    TASK_ADJUSTMENT = "task_adjustment"
    GENERAL_CHAT = "general_chat"


class MessageRole(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    ACTION_REQUEST = "action_request"


class ActionStatus(str, Enum):
    """操作状态"""
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Action(str, Enum):
    """操作类型"""
    CREATE_GOAL = "create_goal"
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    CREATE_EVENT = "create_event"
    UPDATE_EVENT = "update_event"
    DELETE_EVENT = "delete_event"


# 对话会话相关 Schema
class ConversationBase(BaseModel):
    """对话会话基础模型"""
    title: Optional[str] = Field(None, max_length=200, description="对话标题")
    conversation_type: ConversationType = Field(default=ConversationType.GOAL_PLANNING, description="对话类型")


class ConversationCreate(ConversationBase):
    """创建对话会话"""
    pass


class ConversationUpdate(BaseModel):
    """更新对话会话"""
    title: Optional[str] = Field(None, max_length=200, description="对话标题")
    status: Optional[ConversationStatus] = Field(None, description="状态")
    context_summary: Optional[str] = Field(None, description="对话摘要")
    context_json: Optional[dict] = Field(None, description="完整上下文数据")


class ConversationResponse(ConversationBase):
    """对话会话响应"""
    id: int
    user_id: int
    status: ConversationStatus
    related_goal_id: Optional[int] = None
    related_plan_id: Optional[int] = None
    context_summary: Optional[str] = None
    context_json: Optional[dict] = None
    message_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 对话消息相关 Schema
class MessageBase(BaseModel):
    """消息基础模型"""
    role: MessageRole = Field(..., description="角色")
    message_type: MessageType = Field(default=MessageType.TEXT, description="消息类型")
    content: str = Field(..., description="消息内容")
    content_json: Optional[dict] = Field(None, description="结构化内容数据")


class MessageCreate(MessageBase):
    """创建消息"""
    model_used: Optional[str] = Field(None, max_length=50, description="使用的AI模型")
    tokens_used: Optional[int] = Field(default=0, ge=0, description="消耗的token数")


class MessageResponse(MessageBase):
    """消息响应"""
    id: int
    conversation_id: int
    sequence: int
    model_used: Optional[str] = None
    tokens_used: int
    user_feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 对话操作相关 Schema
class ActionBase(BaseModel):
    """操作基础模型"""
    action_type: Action = Field(..., description="操作类型")
    description: Optional[str] = Field(None, max_length=500, description="操作描述")
    action_data: Optional[dict] = Field(None, description="操作数据")


class ActionCreate(ActionBase):
    """创建操作"""
    pass


class ActionResponse(ActionBase):
    """操作响应"""
    id: int
    message_id: int
    conversation_id: int
    status: ActionStatus
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    result_message: Optional[str] = None
    executed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 请求和响应包装类
class ConversationListResponse(BaseModel):
    """对话列表响应"""
    total: int
    items: list[ConversationResponse]


class MessageListResponse(BaseModel):
    """消息列表响应"""
    total: int
    items: list[MessageResponse]
