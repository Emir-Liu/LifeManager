# LLM日历助手

通过自然语言管理Google Calendar日程的LLM助手。

## 功能特性

- 自然语言交互: 使用日常语言管理日程
- 智能意图识别: 自动理解用户需求
- Function Calling: 通过LangChain工具调用日历API
- 多种操作: 查询、创建、更新、删除事件

## 目录结构

```
llm/llm_function_call/
├── agent/
│   ├── calendar_agent.py     # 日历助手Agent
│   └── __init__.py
├── main.py                  # 交互式命令行入口
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
# 安装LLM Function Call依赖
pip install -r llm/llm_function_call/requirements.txt

# 安装Calendar模块依赖
pip install -r calendar/requirements.txt
```

### 2. 配置Google Calendar凭证

将Google Calendar的OAuth凭证文件放置在:
```
calendar/providers/google_calendar/service/desktop_client_secret_*.json
```

### 3. 运行交互式命令行

```bash
python llm/llm_function_call/main.py
```

## 使用示例

### 交互式对话

```bash
$ python llm/llm_function_call/main.py

==============================================================
LLM日历助手
支持通过自然语言管理Google Calendar日程
==============================================================

你: 帮我查询今天有什么安排
助手: 今天您有以下安排:
- 10:00-11:00 团队会议 (会议室A)
- 14:00-15:00 客户会议 (线上)

你: 明天上午10点到11点开一个团队会议
助手: 已成功创建事件: 团队会议
时间: 2024-03-12 10:00-11:00

你: 把明天下午3点的会议改到4点
助手: 已更新会议时间: 2024-03-12 16:00-17:00
```

### 编程方式使用

```python
from llm.llm_function_call.agent.calendar_agent import create_calendar_agent

# 导入并设置日历提供者
import calendar.providers.google_calendar

# 创建Agent
agent = create_calendar_agent(model="gpt-4", temperature=0)

# 查询今日日程
result = agent.invoke({"input": "帮我查询今天有什么安排"})
print(result['output'])

# 创建新事件
result = agent.invoke({
    "input": "明天上午10点到11点开一个团队会议"
})
print(result['output'])

# 更新事件
result = agent.invoke({
    "input": "把明天下午3点的会议改到4点"
})
print(result['output'])

# 删除事件
result = agent.invoke({
    "input": "删除下周二的健身预约"
})
print(result['output'])
```

### 自定义配置

```python
from llm.llm_function_call.agent.calendar_agent import create_calendar_agent_with_config

# 创建带自定义配置的Agent
agent = create_calendar_agent_with_config(
    model="gpt-4",
    temperature=0,
    max_iterations=15,
    max_execution_time=300,
    return_intermediate_steps=True
)

result = agent.invoke({"input": "查询今天的安排"})

# 查看中间步骤
if 'intermediate_steps' in result:
    for step in result['intermediate_steps']:
        print(f"工具调用: {step[0]}")
        print(f"执行结果: {step[1]}")
```

## 支持的操作

### 查询相关
- 查询今日/本周/本月日程
- 按时间范围查询
- 按关键词搜索
- 查询所有日历的事件

### 创建事件
- 指定时间和标题创建
- 添加描述和地点
- 邀请参与者
- 设置提醒

### 更新事件
- 修改时间
- 修改标题/描述/地点
- 添加/删除参与者

### 删除事件
- 按事件ID删除
- 按描述识别删除

### 日历管理
- 查询日历列表
- 跨日历同步事件

## 常见问题

### Q: 如何配置Google Calendar凭证?

A: 需要在Google Cloud Console创建OAuth客户端,下载凭证文件,并放置到指定目录。首次运行会自动在浏览器中授权。

### Q: 支持哪些LLM模型?

A: 支持OpenAI的GPT-3.5、GPT-4等模型。可以在创建Agent时通过`model`参数指定。

### Q: 如何添加新的日历提供者?

A: 实现`CalendarProvider`接口并注册到工厂即可。详见`calendar/README.md`。

### Q: 时间格式要求是什么?

A: 使用ISO 8601格式 (RFC3339),例如: `2024-03-11T10:00:00`。LLM会自动处理自然语言到标准格式的转换。

## 注意事项

1. **API配额**: 注意Google Calendar API的调用配额限制
2. **时区处理**: 确保时间格式包含正确的时区信息
3. **错误处理**: 网络或API错误会被捕获并友好提示
4. **凭证安全**: 妥善保管OAuth凭证文件

## 许可证

MIT License
