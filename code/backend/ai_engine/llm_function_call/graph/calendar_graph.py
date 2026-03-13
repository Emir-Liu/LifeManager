"""日历助手 LangGraph 统一导出模块

提供便捷的接口来使用 LangGraph 实现的日历助手
"""

from langchain_core.messages import HumanMessage, AIMessage
from .builder import build_calendar_graph
from typing import Iterator, Optional
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver


class CalendarGraph:
    """日历助手 LangGraph 包装类"""

    def __init__(self):
        """初始化日历助手"""
        self.memory = MemorySaver()
        self.graph = build_calendar_graph()
        self.app = self.graph.compile(checkpointer=self.memory)
        self.thread_id = "default_thread"

    def invoke(self, input_text: str, thread_id: Optional[str] = None) -> dict:
        """同步调用图

        Args:
            input_text: 用户输入文本
            thread_id: 会话线程ID，用于区分不同会话

        Returns:
            完整的状态字典，包含消息历史
        """
        if thread_id:
            self.thread_id = thread_id

        config = {"configurable": {"thread_id": self.thread_id}}
        result = self.app.invoke(
            {"messages": [HumanMessage(content=input_text)]},
            config
        )
        return result

    def stream(self, input_text: str, stream_mode: str = "updates", thread_id: Optional[str] = None):
        """流式输出

        Args:
            input_text: 用户输入文本
            stream_mode: 流式模式 ("values" 或 "updates")
            thread_id: 会话线程ID

        Yields:
            流式输出事件
        """
        if thread_id:
            self.thread_id = thread_id

        config = {"configurable": {"thread_id": self.thread_id}}
        for event in self.app.stream(
            {"messages": [HumanMessage(content=input_text)]},
            config,
            stream_mode=stream_mode
        ):
            yield event

    def get_graph_ascii(self) -> str:
        """获取图的 ASCII 表示

        Returns:
            图的 ASCII 字符串
        """
        return self.graph.get_graph().print_ascii()

    def get_graph_mermaid(self) -> str:
        """获取图的 Mermaid 格式

        Returns:
            图的 Mermaid 格式字符串
        """
        return self.graph.get_graph().print_mermaid()

    def get_graph_png(self, output_path: str):
        """导出图结构为 PNG 图片

        Args:
            output_path: 输出文件路径
        """
        try:
            self.graph.get_graph().draw_mermaid_png(output_file_path=output_path)
            print(f"图结构已导出到: {output_path}")
        except Exception as e:
            print(f"导出图失败: {e}")


# 便捷函数
def create_calendar_graph() -> CalendarGraph:
    """创建日历助手图实例

    Returns:
        CalendarGraph 实例
    """
    return CalendarGraph()
