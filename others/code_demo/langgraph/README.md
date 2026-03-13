# 最简单的 LangGraph Demo

这是一个最基础的 LangGraph 示例，展示如何构建一个包含系统提示词的对话图。

## 功能特性

- ✅ 系统提示词支持：在每次对话中自动包含系统提示词
- ✅ 状态管理：使用 TypedDict 定义图的状态
- ✅ 单节点图：展示最简单的图结构
- ✅ 交互式对话：支持持续对话，输入 'quit' 或 'exit' 退出

## 代码结构

### 1. 定义状态类型
```python
class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "messages"]
```

### 2. 定义系统提示词
```python
SYSTEM_PROMPT = """你是一个友好的AI助手，可以帮助用户解答各种问题。
请用简洁、清晰的方式回答用户的问题。"""
```

### 3. 定义节点函数
```python
def agent_node(state):
    # 在消息列表前添加系统提示词
    messages = state.get("messages", [])
    messages_with_system = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    return {"messages": [llm.invoke(messages_with_system)]}
```

### 4. 构建图
```python
graph = StateGraph(GraphState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.add_edge("agent", END)
app = graph.compile()
```

### 5. 调用图
```python
result = app.invoke({"messages": [HumanMessage(content=user_input)]})
print(result['messages'][-1].content)
```

## 运行方式

```bash
cd /home/ubuntu/project/LifeManager/others/code_demo/langgraph
python3 simple_graph_demo.py
```

## 配置

确保在 `../../llm/llm_single/config/.env` 文件中配置了正确的 LLM 参数：

```env
LLM_MODEL_NAME=你的模型名称
LLM_MODEL_BASE_URL=你的API地址
LLM_MODEL_API_KEY=你的API密钥
LLM_MODEL_API_TYPE=openai
```

## 系统提示词说明

系统提示词在每次 LLM 调用时都会自动包含，确保助手的行为一致性。你可以修改 `SYSTEM_PROMPT` 变量来改变助手的行为。
