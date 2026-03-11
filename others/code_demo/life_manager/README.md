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
│  │  - quick_add_event    快速添加事件                       │  │
│  │  - list_calendars     查询日历列表                       │  │
│  │  - sync_events        跨日历同步                         │  │
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
│  │  + quick_add()                                          │  │
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
others/code_demo/life_manager
├── calendar/
│   ├── core/
│   │   ├── interfaces.py              # 日历提供者接口定义
│   │   ├── models.py                  # 统一数据模型(Event, Calendar等)
│   │   └── manager.py                 # 日历管理器(多日历聚合)
│   │
│   ├── providers/
│   │   ├── google_calendar/
│   │   │   ├── service/
│   │   │   │   ├── events_service.py      # 事件CRUD服务
│   │   │   │   └── calendar_service.py    # 日历服务
│   │   │   ├── auth/
│   │   │   │   └── oauth_handler.py       # OAuth认证处理
│   │   │   └── provider.py               # Google实现CalendarProvider
│   └── factory.py                       # 日历提供者工厂类
│
├── llm/
│   ├── llm_single/
│   │   ├── utils/
│   │   │   └── llm_operator.py        # LLM操作类封装
│   │   └── config/
│   │       └── config.py              # 配置管理
│   │
│   └── llm_function_call/
│       ├── tools/
│       │   └── calendar_tools.py      # 统一日历工具定义(@tool)
│       ├── agent/
│       │   └── calendar_agent.py      # 日历助手Agent
│       └── main.py                    # 交互式运行入口
│
└── README.md
```

## 技术栈

### AI层
- **LangChain**: Agent框架、工具编排
- **OpenAI API**: LLM模型提供
- **Function Calling**: 工具调用协议

### 日历层
- **统一抽象层**: 多日历服务抽象接口
- **Google Calendar API**: Google日历数据源
- **Microsoft Graph API**: Outlook日历数据源
- **CalDAV / EventKit**: Apple日历数据源
- **OAuth 2.0**: 跨平台认证机制
- **google-api-python-client**: Google API客户端
- **msal**: Microsoft Authentication Library

## 实现步骤

### 1. 设计日历抽象层接口
定义统一的日历服务接口,支持多日历后端扩展

```python
# calendar/core/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Optional
from core.models import Event, Calendar

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

### 2. 实现Google Calendar提供者
✅ 已完成 - `calendar/providers/google_calendar/provider.py`

### 3. 实现日历提供者工厂
通过工厂模式动态创建不同日历提供者实例

```python
# calendar/factory.py
from calendar.core.interfaces import CalendarProvider
from calendar.providers.google_calendar.provider import GoogleCalendarProvider
from calendar.providers.outlook.provider import OutlookProvider

class CalendarProviderFactory:
    """日历提供者工厂"""
    
    @staticmethod
    def create(provider_type: str, config: dict) -> CalendarProvider:
        """创建日历提供者实例"""
        providers = {
            'google': GoogleCalendarProvider,
            'outlook': OutlookProvider,
            'apple': AppleCalendarProvider
        }
        
        provider_class = providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        return provider_class(**config)
```

### 4. 实现多日历管理器
支持多日历聚合查询和跨平台同步

```python
# calendar/core/manager.py
from typing import List, Dict
from calendar.core.interfaces import CalendarProvider
from calendar.core.models import Event

class CalendarManager:
    """多日历管理器"""
    
    def __init__(self, providers: Dict[str, CalendarProvider]):
        self.providers = providers
    
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

### 5. 定义统一的LLM工具
使用抽象层接口,支持多日历操作

```python
# llm/llm_function_call/tools/calendar_tools.py
from langchain.tools import tool
from calendar.factory import CalendarProviderFactory
from calendar.core.manager import CalendarManager

# 初始化多日历管理器
providers = {
    'google': CalendarProviderFactory.create('google', config),
    'outlook': CalendarProviderFactory.create('outlook', config)
}
manager = CalendarManager(providers)

@tool
def list_events(provider: str = "google", calendar_id: str = "primary", 
               start_time: str = None, end_time: str = None):
    """查询事件列表
    
    Args:
        provider: 日历提供者 (google/outlook/apple)
        calendar_id: 日历ID
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
    """
    return manager.providers[provider].list_events(calendar_id, start_time, end_time)

@tool
def create_event(provider: str, summary: str, start_time: str, 
                end_time: str, description: str = ""):
    """创建新事件"""
    # ... 实现细节
    pass

@tool
def sync_event(summary: str, start_time: str, end_time: str, 
               targets: List[str]):
    """跨日历同步事件
    
    Args:
        targets: 目标日历提供者列表,如 ["google", "outlook"]
    """
    # ... 实现细节
    pass
```

### 6. 增加大模型调用的接口
✅ 已完成 - `llm/llm_single/utils/llm_operator.py`

### 7. 增加大模型流式输出的接口
✅ 已完成 - `llm/llm_single/utils/llm_operator.py` (stream_chat方法)

## 使用示例

### 多日历配置
```python
# 初始化多日历管理器
from calendar.factory import CalendarProviderFactory
from calendar.core.manager import CalendarManager

providers = {
    'google': CalendarProviderFactory.create('google', {
        'credentials_path': 'path/to/credentials.json',
        'token_path': 'path/to/token.json'
    }),
    'outlook': CalendarProviderFactory.create('outlook', {
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret'
    })
}
manager = CalendarManager(providers)
```

### 交互式对话
```python
from llm_function_call.agent.calendar_agent import create_calendar_agent

agent = create_calendar_agent()

# 查询Google日历今日日程
result = agent.invoke({"input": "帮我查询Google日历今天有什么安排"})

# 在Outlook日历创建新事件
result = agent.invoke({"input": "在Outlook日历中明天上午10点到11点开一个团队会议"})

# 跨日历查询
result = agent.invoke({"input": "查询所有日历中下周的会议安排"})

# 跨日历同步事件
result = agent.invoke({"input": "把周五的健身预约同步到Google和Outlook日历"})

# 更新特定日历的事件
result = agent.invoke({"input": "把Google日历中明天下午3点的会议改到4点"})

# 删除事件
result = agent.invoke({"input": "删除Apple日历中下周二的健身预约"})
```

### 编程方式调用
```python
# 聚合查询所有日历事件
events = manager.list_all_events(
    start_time="2024-03-10T00:00:00",
    end_time="2024-03-10T23:59:59"
)

# 跨日历同步事件
event = Event(
    summary="团队会议",
    start_time="2024-03-11T10:00:00",
    end_time="2024-03-11T11:00:00"
)
synced = manager.sync_event(event, targets=["google", "outlook"])
```

## 工作流程

1. **用户输入**: 用户通过前端发送自然语言请求
2. **意图识别**: LLM分析用户意图,决定是否需要调用工具
3. **日历选择**: Agent识别用户指定的日历提供者
4. **函数调用**: Agent选择合适的工具并提取参数
5. **提供者路由**: CalendarManager根据provider参数路由到对应的提供者
6. **执行操作**: 调用特定日历提供者的API (Google/Outlook/Apple)
7. **结果返回**: 将操作结果返回给LLM生成自然语言响应
8. **流式输出**: 响应通过流式接口实时返回给前端

## 扩展新的日历服务

### 1. 实现CalendarProvider接口
```python
# calendar/providers/new_calendar/provider.py
from calendar.core.interfaces import CalendarProvider
from calendar.core.models import Event, Calendar

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
# calendar/factory.py
providers = {
    'google': GoogleCalendarProvider,
    'outlook': OutlookProvider,
    'apple': AppleCalendarProvider,
    'new_calendar': NewCalendarProvider  # 新增
}
```

### 3. 更新工具列表
```python
# llm/llm_function_call/tools/calendar_tools.py
@tool
def list_events(provider: str = "google", ...):
    """查询事件列表
    支持的日历: google, outlook, apple, new_calendar
    """
    return manager.providers[provider].list_events(...)
```

## 核心优势

- **分层设计**: AI层与日历层职责清晰,易于维护和扩展
- **接口抽象**: 通过统一接口支持多种日历服务
- **工厂模式**: 动态创建和切换日历提供者
- **工具化**: 通过Function Calling实现灵活的工具编排
- **可扩展**: 轻松添加新的日历服务,无需修改核心逻辑
- **多日历聚合**: 支持跨日历查询和同步
- **用户友好**: 自然语言交互,指定日历类型即可操作
- **松耦合**: 各日历提供者相互独立,互不影响
