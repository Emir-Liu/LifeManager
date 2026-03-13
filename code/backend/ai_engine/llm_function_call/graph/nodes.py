"""LangGraph 节点函数定义"""

from calendar_engine.tools.calendar_tools import (
    list_events,
    create_event,
    update_event,
    delete_event,
    get_event,
    list_calendars,
    sync_event,
    list_all_events,
    clear_calendar,
    delete_calendar,
    create_calendar,
    get_calendar_details,
    update_calendar,
    list_recurring_events,
    create_recurring_event,
    update_recurring_event,
    delete_recurring_event,
    get_recurring_event_instances
)
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from .state import CalendarState


# 定义工具列表
CALENDAR_TOOLS = [
    list_events,
    create_event,
    update_event,
    delete_event,
    get_event,
    list_calendars,
    sync_event,
    list_all_events,
    clear_calendar,
    delete_calendar,
    create_calendar,
    get_calendar_details,
    update_calendar,
    list_recurring_events,
    create_recurring_event,
    update_recurring_event,
    delete_recurring_event,
    get_recurring_event_instances
]


def create_tool_node() -> ToolNode:
    """创建工具节点

    Returns:
        ToolNode 实例，包含所有日历工具
    """
    return ToolNode(CALENDAR_TOOLS)
