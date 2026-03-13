#!/usr/bin/env python3
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, '../../llm/llm_single'))
from config.config import LLMConfig
from utils.llm_operator import LLMOperator

# 系统提示词
SYSTEM_PROMPT = """你是一个友好的AI助手，可以帮助用户解答各种问题。
请用简洁、清晰的方式回答用户的问题。"""

class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "messages"]

llm = LLMOperator(LLMConfig()).get_llm()

def agent_node(state):
    # 在消息列表前添加系统提示词
    messages = state.get("messages", [])
    messages_with_system = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    return {"messages": [llm.invoke(messages_with_system)]}

graph = StateGraph(GraphState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.add_edge("agent", END)
app = graph.compile()

if __name__ == "__main__":
    print("简单的 LangGraph Demo - 输入 'quit' 或 'exit' 退出")
    print(f"系统提示词: {SYSTEM_PROMPT}")
    print("-" * 50)

    while True:
        user_input = input("你: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit']:
            print("再见!")
            break

        result = app.invoke({"messages": [HumanMessage(content=user_input)]})
        print(f"助手: {result['messages'][-1].content}")
