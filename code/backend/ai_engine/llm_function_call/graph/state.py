"""LangGraph State 定义"""

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CalendarState(TypedDict):
    """日历助手的 State 类型定义

    包含:
    - messages: 消息历史，使用 add_messages 自动合并
    """
    messages: Annotated[list[BaseMessage], add_messages]
