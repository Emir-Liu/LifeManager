# LLM模块

大模型操作模块,支持多种LLM提供商(OpenAI、百炼等)。

## 功能特性

- 多LLM支持: OpenAI、百炼等
- 灵活配置: 通过环境变量配置模型参数
- 流式/非流式: 支持两种调用方式
- 错误重试: 内置自动重试机制

## 目录结构

```
llm/
├── config/
│   ├── config.py          # 配置管理类
│   └── .env.demo        # 环境变量示例
├── utils/
│   └── llm_operator.py  # LLM操作类
├── llm_single/          # 单LLM调用示例
├── llm_function_call/   # LLM Function Call实现
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r llm/requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件:

```bash
cp llm/config/.env.demo llm/config/.env
```

编辑`.env`文件,填入你的配置:

```env
LLM_MODEL_NAME=gpt-4
LLM_MODEL_BASE_URL=  # 可选,不填则使用OpenAI官方
LLM_MODEL_API_KEY=your-api-key-here
LLM_MODEL_API_TYPE=openai
```

### 3. 使用LLM操作类

```python
from llm.config.config import LLMConfig
from llm.utils.llm_operator import LLMOperator

# 加载配置
llm_config = LLMConfig()
llm_config.show_config()

# 创建LLM操作实例
llm_operator = LLMOperator(llm_config)

# 非流式对话
response = llm_operator.chat("你是谁?")
print(response.content)

# 流式对话
for chunk in llm_operator.stream_chat("介绍一下你自己"):
    print(chunk, end='', flush=True)
```

## API文档

### LLMConfig

配置管理类,从环境变量加载LLM配置。

**参数:**
- `config_path`: 环境变量文件路径,默认为`./config/.env`

**属性:**
- `model_name`: 模型名称
- `base_url`: API基础URL
- `api_key`: API密钥
- `api_type`: API类型 (openai/bailian)

**方法:**
- `show_config()`: 打印当前配置

### LLMOperator

LLM操作类,封装LangChain的ChatOpenAI。

**初始化参数:**
- `llm_config`: LLMConfig实例

**方法:**

#### get_llm()
获取底层LangChain LLM实例。

#### chat(user_input, system_prompt=None)
非流式对话。

**参数:**
- `user_input`: 用户输入
- `system_prompt`: 系统提示词(可选)

**返回:** AIMessage对象

#### stream_chat(user_input, system_prompt=None)
流式对话。

**参数:**
- `user_input`: 用户输入
- `system_prompt`: 系统提示词(可选)

**返回:** 流式内容生成器

## 支持的LLM提供商

### OpenAI

```env
LLM_MODEL_NAME=gpt-4
LLM_MODEL_API_TYPE=openai
```

### 百炼 (千问)

```env
LLM_MODEL_NAME=qwen3-32b
LLM_MODEL_BASE_URL=your-base-url
LLM_MODEL_API_KEY=your-api-key
LLM_MODEL_API_TYPE=bailian
```

### vLLM本地部署

```env
LLM_MODEL_NAME=qwen3-32b
LLM_MODEL_BASE_URL=http://localhost:8000/v1
LLM_MODEL_API_KEY=dummy
LLM_MODEL_API_TYPE=openai
```

## 示例

### 基础对话

```python
from llm.config.config import LLMConfig
from llm.utils.llm_operator import LLMOperator

config = LLMConfig()
operator = LLMOperator(config)

response = operator.chat("你好")
print(response.content)
```

### 带系统提示的对话

```python
response = operator.chat(
    user_input="帮我写一首诗",
    system_prompt="你是一位著名的诗人"
)
```

### 流式输出

```python
print("AI: ", end='', flush=True)
for chunk in operator.stream_chat("讲一个故事"):
    print(chunk, end='', flush=True)
print()
```

### 直接使用LangChain LLM

```python
llm = operator.get_llm()
message = llm.invoke("你好")
print(message)
```

## 注意事项

1. **API密钥安全**: 不要将`.env`文件提交到版本控制
2. **API配额**: 注意各LLM服务的调用配额限制
3. **网络连接**: 确保可以访问LLM API服务
4. **模型支持**: 不同LLM提供商支持的功能可能不同

## 与Function Call集成

LLM模块与Function Call模块结合,可以实现自然语言调用工具:

```python
from llm.utils.llm_operator import LLMOperator
from calendar.tools.calendar_tools import list_events, create_event

# 创建LLM
config = LLMConfig()
llm = LLMOperator(config).get_llm()

# 创建Agent
from langchain.agents import AgentExecutor, create_tool_calling_agent
tools = [list_events, create_event]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# 自然语言调用
result = executor.invoke({"input": "帮我查询今天有什么安排"})
```

## 许可证

MIT License
