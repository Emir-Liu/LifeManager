"""
日历助手Agent - 已弃用

注意：本项目现在使用LangGraph实现，本文件中的LangChain Agent已不再使用。
请使用 ai_engine/llm_function_call/graph/builder.py 中的LangGraph实现。
"""

# 保留空的导入以避免破坏现有代码
from langchain.agents import create_agent


def create_calendar_agent():
    """创建日历助手Agent（已弃用）

    已弃用：请使用LangGraph实现（graph/builder.py）
    """
    raise DeprecationWarning(
        "create_calendar_agent 已弃用。请使用 ai_engine/llm_function_call/graph.builder.create_calendar_graph()"
    )


def create_calendar_agent_with_config(
    model: str = "gpt-4",
    temperature: float = 0,
    max_iterations: int = 15,
    max_execution_time: float = 300,
    return_intermediate_steps: bool = False
):
    """创建日历助手Agent(带完整配置) - 已弃用

    已弃用：请使用LangGraph实现（graph/builder.py）
    """
    raise DeprecationWarning(
        "create_calendar_agent_with_config 已弃用。请使用 ai_engine/llm_function_call/graph.builder.create_calendar_graph()"
    )
