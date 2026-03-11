# Calendar Module

日历抽象层,支持多种日历服务(Google Calendar, Outlook, Apple Calendar等)。

## 功能特性

- 统一接口: 提供一致的API访问不同日历服务
- 多日历支持: 同时管理多个日历提供者
- 跨平台同步: 轻松在不同日历间同步事件
- LLM集成: 提供LangChain工具函数,支持Function Calling

## 目录结构

```
calendar/
├── core/                    # 核心抽象层
│   ├── interface.py         # 日历提供者接口
│   ├── models.py           # 数据模型(Event, Calendar)
│   ├── factory.py          # 工厂类
│   └── manager.py         # 多日历管理器
├── providers/             # 日历提供者实现
│   ├── google_calendar/    # Google Calendar提供者
│   │   ├── core/         # Google Calendar核心客户端
│   │   ├── service/      # Google Calendar服务
│   │   └── provider.py   # 提供者实现
├── tools/               # LLM工具函数
│   └── calendar_tools.py
└── requirements.txt
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r calendar/requirements.txt
```

### 2. 配置Google Calendar

```python
from calendar.core.factory import CalendarProviderFactory

# 导入Google Calendar提供者(自动注册)
import calendar.providers.google_calendar

# 创建Google Calendar提供者
google_provider = CalendarProviderFactory.create('google', {
    'credentials_path': 'path/to/credentials.json',
    'token_path': 'path/to/token.json'
})

# 列出日历
calendars = google_provider.list_calendars()
for cal in calendars:
    print(f"{cal.summary} (ID: {cal.id})")

# 查询事件
events = google_provider.list_events(
    calendar_id='primary',
    start_time='2024-03-10T00:00:00',
    end_time='2024-03-10T23:59:59'
)

# 创建事件
from calendar.core.models import Event
event = google_provider.create_event(
    calendar_id='primary',
    event=Event(
        id='',
        calendar_id='primary',
        summary='团队会议',
        start_time='2024-03-11T10:00:00',
        end_time='2024-03-11T11:00:00'
    )
)
```

### 3. 使用多日历管理器

```python
from calendar.core.factory import CalendarProviderFactory

# 导入提供者(自动注册)
import calendar.providers.google_calendar

# 创建多日历管理器
manager = CalendarProviderFactory.create_manager({
    'google': {
        'credentials_path': 'path/to/google_credentials.json',
        'token_path': 'path/to/google_token.json'
    }
})

# 聚合查询所有日历
events = manager.list_all_events(
    start_time='2024-03-10T00:00:00',
    end_time='2024-03-10T23:59:59'
)

# 跨日历同步事件
synced = manager.sync_event(
    event=Event(...),
    target_providers=['google']
)
```

### 4. 使用LLM工具函数

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from calendar.tools.calendar_tools import (
    list_events,
    create_event,
    update_event,
    delete_event
)

# 定义工具列表
tools = [list_events, create_event, update_event, delete_event]

# 创建Agent
llm = ChatOpenAI(model="gpt-4")
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# 使用自然语言管理日历
result = executor.invoke({"input": "帮我查询今天有什么安排"})
result = executor.invoke({"input": "明天上午10点到11点开一个团队会议"})
```

## API文档

### CalendarProvider接口

所有日历提供者必须实现以下方法:

- `list_events(calendar_id, start_time, end_time)` - 查询事件列表
- `create_event(calendar_id, event)` - 创建事件
- `update_event(event_id, event)` - 更新事件
- `delete_event(event_id)` - 删除事件
- `get_event(event_id)` - 获取事件详情
- `list_calendars()` - 获取日历列表

### 数据模型

#### Event
```python
@dataclass
class Event:
    id: str
    calendar_id: str
    summary: str
    start_time: str  # ISO格式
    end_time: str    # ISO格式
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    status: Optional[str] = None
```

#### Calendar
```python
@dataclass
class Calendar:
    id: str
    summary: str
    description: Optional[str] = None
    primary: bool = False
    color_id: Optional[str] = None
```

## 扩展新的日历服务

### 1. 实现CalendarProvider接口

```python
from calendar.core.interface import CalendarProvider

class NewCalendarProvider(CalendarProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    # 实现所有抽象方法...
```

### 2. 注册到工厂

```python
from calendar.core.factory import CalendarProviderFactory
from calendar.providers.new_calendar.provider import NewCalendarProvider

# 在__init__.py中注册
CalendarProviderFactory.register('new_calendar', NewCalendarProvider)
```

### 3. 使用新提供者

```python
provider = CalendarProviderFactory.create('new_calendar', {
    'api_key': 'your_api_key'
})
```

## 已实现的提供者

| 提供者 | 状态 | 文档 |
|--------|------|------|
| Google Calendar | ✅ 已实现 | [Google Calendar API](https://developers.google.com/calendar) |
| Outlook | ⏳ 待实现 | [Microsoft Graph API](https://docs.microsoft.com/graph/api/resources/calendar) |
| Apple Calendar | ⏳ 待实现 | [CalDAV](https://datatracker.ietf.org/doc/html/rfc4791) |

## 注意事项

1. **认证文件**: Google Calendar需要OAuth认证文件
2. **时区处理**: 所有时间使用ISO 8601格式(RFC3339)
3. **错误处理**: API调用失败会抛出异常,需要捕获处理
4. **配额限制**: 注意各日历API的调用配额限制

## 许可证

MIT License
