# AI日程管理App架构设计

## 架构概述

本项目是一个基于LLM的智能日程管理系统,采用分层架构设计,通过Function Calling机制实现AI与多种日历服务的无缝集成。系统支持Google Calendar、Outlook、Apple Calendar等多种日历后端,通过抽象层实现统一接口。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端 (Frontend)                          │
│                  Web / 移动端 / 桌面端                        │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      AI服务层 (AI Layer)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              LLM核心 (LLM Core)                        │  │
│  │  - 意图识别 (Intent Recognition)                        │  │
│  │  - 参数提取 (Parameter Extraction)                     │  │
│  │  - 响应生成 (Response Generation)                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Function Calling (LangChain)                   │  │
│  │  - 工具编排 (Tool Orchestration)                       │  │
│  │  - Agent执行器 (Agent Executor)                        │  │
│  │  - 函数调用循环 (Function Call Loop)                   │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Unified Calendar Tools (@tool装饰器)          │  │
│  │  - list_events        查询事件列表                      │  │
│  │  - create_event       创建新事件                         │  │
│  │  - update_event       更新已有事件                       │  │
│  │  - delete_event       删除事件                           │  │
│  │  - get_event          查询事件详情                       │  │
│  │  - list_calendars     查询日历列表                       │  │
│  │  - sync_event        跨日历同步                         │  │
│  │  - list_all_events   聚合查询所有日历                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                   日历抽象层 (Calendar Abstraction)           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         CalendarProvider (提供者接口)                   │  │
│  │  + list_events()                                        │  │
│  │  + create_event()                                       │  │
│  │  + update_event()                                       │  │
│  │  + delete_event()                                       │  │
│  │  + get_event()                                          │  │
│  │  + list_calendars()                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         CalendarManager (日历管理器)                     │  │
│  │  - 多日历聚合查询                                         │  │
│  │  - 跨平台事件同步                                         │  │
│  │  - 冲突检测与解决                                         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌────────▼─────────┐
│  Google Calendar  │ │   Outlook    │ │   Apple Calendar  │
│      Provider     │ │   Provider   │ │     Provider      │
├───────────────────┤ ├─────────────┤ ├───────────────────┤
│ - EventsService   │ │ - Graph API │ │ - EventKit        │
│ - CalendarService  │ │ - OAuth 2.0 │ │ - Local Sync      │
│ - OAuth Handler    │ │             │ │                   │
└───────────────────┘ └─────────────┘ └───────────────────┘
          │                   │                   │
┌─────────▼─────────┐ ┌──────▼──────┐ ┌────────▼─────────┐
│ Google Calendar   │ │ Microsoft   │ │   iCloud / CalDAV│
│      API          │ │   Graph API │ │      API         │
└───────────────────┘ └─────────────┘ └───────────────────┘
```

## 目录结构

```
backend/
├── calendar_engine/                      # 日历引擎模块
│   ├── core/                            # 核心抽象层
│   │   ├── interface.py                  # 日历提供者接口定义
│   │   ├── models.py                    # 统一数据模型(Event, Calendar等)
│   │   ├── factory.py                   # 日历提供者工厂类
│   │   └── manager.py                   # 日历管理器(多日历聚合)
│   │
│   ├── providers/                        # 日历提供者实现
│   │   └── google_calendar/             # Google Calendar提供者
│   │       ├── core/                    # 核心功能
│   │       │   ├── base_client.py         # Google Calendar API基础客户端
│   │       │   ├── google_calendar_client.py  # 统一客户端
│   │       │   └── config.py             # 配置文件
│   │       ├── service/                  # API服务封装
│   │       │   ├── events_service.py     # 事件CRUD服务
│   │       │   ├── calendars_service.py  # 日历服务
│   │       │   ├── calendarlist_service.py  # 日历列表服务
│   │       │   ├── acl_service.py        # 访问控制服务
│   │       │   ├── freebusy_service.py   # 忙闲查询服务
│   │       │   ├── settings_service.py   # 设置服务
│   │       │   ├── channels_service.py   # 频道服务
│   │       │   └── examples.py          # 使用示例
│   │       └── provider.py                # Google实现CalendarProvider
│   │
│   ├── tools/                            # LangChain工具
│   │   └── calendar_tools.py            # 统一日历工具定义(@tool)
│   └── requirements.txt                  # 日历引擎依赖
│
├── ai_engine/                           # AI引擎模块
│   ├── config/                           # 配置管理
│   │   └── config.py                  # LLM配置类
│   ├── utils/                            # 工具类
│   │   └── llm_operator.py             # LLM操作类封装
│   ├── llm_function_call/                # Function Call模块
│   │   ├── agent/                     # Agent定义
│   │   │   ├── __init__.py
│   │   │   └── calendar_agent.py       # 日历助手Agent
│   │   ├── main.py                    # 交互式运行入口
│   │   └── requirements.txt           # Function Call依赖
│   └── requirements.txt                  # AI引擎依赖
│
├── requirements.txt                      # 项目总依赖
└── README.md                           # 本文档
```

## 技术栈

### AI层
- **LangChain**: Agent框架、工具编排 (langchain>=0.1.0, langchain-core>=0.1.0)
- **LangChain OpenAI**: OpenAI API集成 (langchain-openai>=0.0.5)
- **OpenAI Compatible APIs**: 支持OpenAI、通义千问等多种模型
- **Function Calling**: 工具调用协议

### 日历层
- **统一抽象层**: 多日历服务抽象接口
- **Google Calendar API**: Google日历数据源
- **OAuth 2.0**: Google认证机制
- **google-api-python-client**: Google API客户端 (>=2.100.0)
- **google-auth**: Google认证库 (>=2.23.0)
- **google-auth-oauthlib**: OAuth流程库 (>=1.0.0)

### 工具库
- **python-dotenv**: 环境变量管理 (>=1.0.0)
- **python-dateutil**: 日期时间处理 (>=2.8.2)

## 核心模块说明

### 1. calendar_engine (日历引擎)

#### 核心抽象层 (core/)
- **interface.py**: 定义 `CalendarProvider` 抽象接口,规范所有日历提供者的行为
- **models.py**: 定义统一的数据模型,包括 `Event`、`Calendar` 等
- **factory.py**: 工厂类,用于动态创建不同类型的日历提供者
- **manager.py**: 多日历管理器,支持跨日历查询和同步

#### Google Calendar 提供者 (providers/google_calendar/)
- **provider.py**: 实现 `CalendarProvider` 接口,提供 Google Calendar 的完整功能
- **core/base_client.py**: 封装 Google OAuth 认证和 API 客户端初始化
- **core/google_calendar_client.py**: 统一的客户端接口,整合所有服务
- **service/**: 细粒度的 API 服务封装
  - events_service.py: 事件 CRUD 操作
  - calendars_service.py: 日历元数据操作
  - calendarlist_service.py: 日历列表操作
  - acl_service.py: 访问权限控制
  - freebusy_service.py: 忙闲时间查询
  - settings_service.py: 日历设置
  - channels_service.py: 推送频道

#### 工具层 (tools/)
- **calendar_tools.py**: 使用 `@tool` 装饰器定义 LangChain 工具,包括:
  - list_events: 查询特定日历的事件
  - create_event: 创建新事件
  - update_event: 更新事件
  - delete_event: 删除事件
  - get_event: 获取事件详情
  - list_calendars: 查询日历列表
  - sync_event: 跨日历同步事件
  - list_all_events: 聚合查询所有日历

### 2. ai_engine (AI 引擎)

#### 配置管理 (config/)
- **config.py**: `LLMConfig` 类,管理 LLM 相关配置:
  - 模型名称 (支持自定义和标准模型)
  - API 基础 URL
  - API 密钥
  - 温度参数
  - 从 .env 文件加载配置

#### 工具类 (utils/)
- **llm_operator.py**: `LLMOperator` 类,封装 LLM 操作:
  - get_llm(): 获取配置好的 LLM 实例
  - chat(): 单轮对话
  - stream_chat(): 流式对话输出
  - 支持异步调用

#### Function Call 模块 (llm_function_call/)
- **agent/calendar_agent.py**: 创建日历助手 Agent
  - 使用 `create_agent` 创建 LangChain Agent
  - 集成所有日历工具
  - 配置系统提示词
  - 支持工具自动调用
- **main.py**: 交互式命令行入口
  - 提供自然语言交互界面
  - 处理用户输入和错误

## 实现步骤

### 1. 设计日历抽象层接口

定义统一的日历服务接口,支持多日历后端扩展:

```python
# calendar_engine/core/interface.py
from abc import ABC, abstractmethod
from typing import List, Optional
from calendar_engine.core.models import Event, Calendar

class CalendarProvider(ABC):
    """日历提供者抽象接口"""

    @abstractmethod
    def list_events(self, calendar_id: str, start_time: str, end_time: str) -> List[Event]:
        """获取事件列表"""
        pass

    @abstractmethod
    def create_event(self, calendar_id: str, event: Event) -> Event:
        """创建事件"""
        pass

    @abstractmethod
    def update_event(self, event_id: str, event: Event) -> Event:
        """更新事件"""
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """删除事件"""
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Event:
        """获取事件详情"""
        pass

    @abstractmethod
    def list_calendars(self) -> List[Calendar]:
        """获取日历列表"""
        pass
```

### 2. 实现 Google Calendar 提供者

✅ 已完成 - `calendar_engine/providers/google_calendar/provider.py`

特性:
- OAuth 2.0 认证流程
- 完整的事件 CRUD 操作
- 日历列表和元数据管理
- 访问权限控制
- 忙闲时间查询

### 3. 实现日历提供者工厂

通过工厂模式动态创建不同日历提供者实例:

```python
# calendar_engine/core/factory.py
from calendar_engine.core.interface import CalendarProvider
from calendar_engine.providers.google_calendar.provider import GoogleCalendarProvider

class CalendarProviderFactory:
    """日历提供者工厂"""

    _providers = {}

    @classmethod
    def register(cls, provider_type: str, provider_class: type):
        """注册日历提供者"""
        cls._providers[provider_type] = provider_class

    @classmethod
    def create(cls, provider_type: str, config: dict = None) -> CalendarProvider:
        """创建日历提供者实例"""
        config = config or {}
        provider_class = cls._providers.get(provider_type)

        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider_type}")

        return provider_class(**config)
```

### 4. 实现多日历管理器

支持多日历聚合查询和跨平台同步:

```python
# calendar_engine/core/manager.py
from typing import List, Dict, Optional
from calendar_engine.core.interface import CalendarProvider
from calendar_engine.core.models import Event

class CalendarManager:
    """多日历管理器"""

    def __init__(self, providers: Optional[Dict[str, CalendarProvider]] = None,
                 factory: Optional[CalendarProviderFactory] = None):
        self.factory = factory or CalendarProviderFactory()
        self.providers = providers or {}

    def add_provider(self, provider_type: str, config: dict = None):
        """添加日历提供者"""
        self.providers[provider_type] = self.factory.create(provider_type, config)

    def list_all_events(self, start_time: str, end_time: str) -> List[Event]:
        """聚合查询所有日历的事件"""
        all_events = []
        for provider in self.providers.values():
            calendars = provider.list_calendars()
            for calendar in calendars:
                events = provider.list_events(calendar.id, start_time, end_time)
                all_events.extend(events)
        return sorted(all_events, key=lambda e: e.start_time)

    def sync_event(self, event: Event, target_providers: List[str]) -> List[Event]:
        """跨日历同步事件"""
        synced_events = []
        for provider_name in target_providers:
            provider = self.providers.get(provider_name)
            if provider:
                synced = provider.create_event(event.calendar_id, event)
                synced_events.append(synced)
        return synced_events
```

### 5. 定义统一的 LLM 工具

使用抽象层接口,支持多日历操作:

```python
# calendar_engine/tools/calendar_tools.py
from langchain.tools import tool
from calendar_engine.core.factory import CalendarProviderFactory
from calendar_engine.core.manager import CalendarManager
from calendar_engine.core.models import Event
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# 获取 Google Calendar 配置
def _get_google_calendar_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    credentials_pattern = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH',
                                   'calendar_engine/providers/google_calendar/service/desktop_client_secret_*.json')
    token_path_env = os.getenv('GOOGLE_CALENDAR_TOKEN_PATH',
                              'calendar_engine/providers/google_calendar/service/token.json')

    import glob
    credentials_path_pattern = os.path.join(base_dir, credentials_pattern)
    credentials_files = glob.glob(credentials_path_pattern)
    credentials_path = credentials_files[0] if credentials_files else None
    token_path = os.path.join(base_dir, token_path_env)

    return {
        'credentials_path': credentials_path,
        'token_path': token_path
    }

# 获取提供者实例
def _get_provider(provider: str):
    factory = CalendarProviderFactory()
    if provider == 'google':
        config = _get_google_calendar_config()
        return factory.create(provider, config)
    else:
        return factory.create(provider)

@tool
def list_events(provider: str = "google", calendar_id: str = "primary",
               start_time: str = None, end_time: str = None):
    """查询事件列表"""
    provider_instance = _get_provider(provider)
    return provider_instance.list_events(calendar_id, start_time, end_time)

@tool
def list_all_events(start_time: str, end_time: str):
    """聚合查询所有日历的事件"""
    factory = CalendarProviderFactory()
    providers = {}
    for provider_type in factory.list_providers():
        try:
            providers[provider_type] = _get_provider(provider_type)
        except Exception as e:
            print(f"创建 {provider_type} 提供者失败: {e}")
            continue

    manager = CalendarManager(providers=providers)
    return manager.list_all_events(start_time, end_time)
```

### 6. LLM 配置和操作

✅ 已完成 - `ai_engine/config/config.py` 和 `ai_engine/utils/llm_operator.py`

支持的配置项:
- LLM_MODEL_NAME: 模型名称 (如 gpt-4, qwen3-32b)
- LLM_MODEL_BASE_URL: API 基础 URL
- LLM_MODEL_API_KEY: API 密钥
- LLM_MODEL_API_TYPE: API 类型 (openai/bailian)

## 配置文件

### .env 文件

在项目根目录创建 `.env` 文件:

```bash
# LLM 配置
LLM_MODEL_NAME=gpt-4
LLM_MODEL_BASE_URL=https://api.openai.com/v1
LLM_MODEL_API_KEY=your_api_key_here
LLM_MODEL_API_TYPE=openai

# Google Calendar 配置
GOOGLE_CALENDAR_CREDENTIALS_PATH=calendar_engine/providers/google_calendar/service/desktop_client_secret_*.json
GOOGLE_CALENDAR_TOKEN_PATH=calendar_engine/providers/google_calendar/service/token.json
```

## 使用示例

### 初始化和配置

```python
# 创建日历 Agent
from ai_engine.llm_function_call.agent.calendar_agent import create_calendar_agent

agent = create_calendar_agent()

# 使用 Agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "帮我查询今天有什么安排"}]
})

# 提取响应
if hasattr(result, 'messages') and result.messages:
    last_message = result.messages[-1]
    print(getattr(last_message, 'content', str(last_message)))
```

### 交互式对话

```python
# 运行交互式程序
python -m ai_engine.llm_function_call.main
```

支持的命令示例:
- "帮我查询今天有什么安排"
- "明天上午10点到11点开一个团队会议"
- "查询所有日历中下周的会议安排"
- "把Google日历中明天下午3点的会议改到4点"
- "删除明天下午的会议"

### 编程方式调用

```python
from calendar_engine.core.factory import CalendarProviderFactory
from calendar_engine.core.manager import CalendarManager

# 创建提供者
factory = CalendarProviderFactory()
google_provider = factory.create('google', {
    'credentials_path': 'path/to/credentials.json',
    'token_path': 'path/to/token.json'
})

# 创建管理器
manager = CalendarManager(providers={'google': google_provider})

# 查询事件
events = manager.list_all_events(
    start_time="2024-03-11T00:00:00",
    end_time="2024-03-11T23:59:59"
)
```

## 启动脚本

### 快速启动

项目提供了便捷的启动方式,支持直接通过 Python 模块运行 LLM 日历助手:

```bash
# 方式 1: 使用 Python 模块方式启动(推荐)
python -m ai_engine.llm_function_call.main

# 方式 2: 直接运行入口文件
python ai_engine/llm_function_call/main.py
```

### 启动流程说明

运行上述命令后,程序会执行以下流程:

1. **加载配置**
   - 自动从 `.env` 文件加载 LLM 和 Google Calendar 配置
   - 显示凭证路径信息

2. **初始化日历助手**
   - 使用 LangChain `create_agent` 创建 Agent
   - 集成所有日历工具
   - 加载系统提示词

3. **进入交互模式**
   - 等待用户输入自然语言指令
   - 根据输入自动调用相应工具

4. **处理用户请求**
   - 意图识别和参数提取
   - 调用 Google Calendar API
   - 返回结果并生成响应

### 常用交互命令示例

```
你: 帮我查询今天有什么安排
你: 明天上午10点到11点开一个团队会议
你: 查询所有日历中下周的会议安排
你: 把Google日历中明天下午3点的会议改到4点
你: 删除明天下午的会议
你: quit  # 退出程序
```

### 注意事项

1. **首次使用认证**: 首次运行会自动打开浏览器完成 Google OAuth 授权,授权成功后 token 会保存到 `token.json`
2. **凭证文件**: 确保 Google Calendar 凭证文件已配置在 `calendar_engine/providers/google_calendar/service/` 目录
3. **环境变量**: 确保 `.env` 文件中配置了正确的 API 密钥和路径

## 工作流程

1. **用户输入**: 用户通过前端或命令行发送自然语言请求
2. **意图识别**: LLM 分析用户意图,决定是否需要调用工具
3. **参数提取**: Agent 从用户输入中提取必要的参数
4. **函数调用**: Agent 选择合适的工具并调用
5. **提供者路由**: 根据参数路由到对应的日历提供者
6. **执行操作**: 调用 Google Calendar API 执行操作
7. **结果返回**: 将操作结果返回给 LLM
8. **响应生成**: LLM 生成自然语言响应
9. **流式输出**: 响应通过流式接口实时返回

## 扩展新的日历服务

### 1. 实现 CalendarProvider 接口

```python
# calendar_engine/providers/new_calendar/provider.py
from calendar_engine.core.interface import CalendarProvider
from calendar_engine.core.models import Event, Calendar

class NewCalendarProvider(CalendarProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def list_events(self, calendar_id: str, start_time: str, end_time: str):
        # 实现新日历的查询逻辑
        pass

    def create_event(self, calendar_id: str, event: Event):
        # 实现新日历的创建逻辑
        pass

    # 实现其他抽象方法...
```

### 2. 注册到工厂

```python
# calendar_engine/core/factory.py 或在初始化时注册
from calendar_engine.providers.new_calendar.provider import NewCalendarProvider

CalendarProviderFactory.register('new_calendar', NewCalendarProvider)
```

### 3. 更新工具配置

工具层会自动支持新的提供者,只需在环境配置中提供相应的凭证。

## 核心优势

- **分层设计**: AI 层与日历层职责清晰,易于维护和扩展
- **接口抽象**: 通过统一接口支持多种日历服务
- **工厂模式**: 动态创建和切换日历提供者
- **工具化**: 通过 Function Calling 实现灵活的工具编排
- **可扩展**: 轻松添加新的日历服务,无需修改核心逻辑
- **多日历聚合**: 支持跨日历查询和同步
- **用户友好**: 自然语言交互,指定日历类型即可操作
- **松耦合**: 各日历提供者相互独立,互不影响
- **配置化**: 通过环境变量管理配置,支持多环境部署

## 注意事项

### OAuth 认证

Google Calendar 首次使用时需要完成 OAuth 认证流程:
1. 运行程序会自动打开浏览器进行授权
2. 授权成功后 token 会保存到 `token.json`
3. 后续使用无需重新授权

### 错误处理

系统已集成基础错误处理:
- 404 Not Found: 事件或日历不存在
- 403 Forbidden: 权限不足
- 401 Unauthorized: 认证失败

### 导入路径

项目使用 `calendar_engine` 作为顶级包名,所有导入应使用:
```python
from calendar_engine.core.interface import CalendarProvider
from calendar_engine.providers.google_calendar.provider import GoogleCalendarProvider
```

避免使用旧的包名如 `calendar` 或 `llm`。

## 开发计划

- [x] 实现核心抽象层接口
- [x] 实现 Google Calendar 提供者
- [x] 实现工厂模式
- [x] 实现多日历管理器
- [x] 定义 LangChain 工具
- [x] 实现 LLM Operator
- [x] 实现 Calendar Agent
- [ ] 实现 Outlook Calendar 提供者
- [ ] 实现 Apple Calendar 提供者
- [ ] 添加单元测试
- [ ] 添加日志系统
- [ ] 性能优化
- [ ] 添加缓存机制
