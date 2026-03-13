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
- `clear_calendar(calendar_id)` - 清空日历中的所有事件
- `delete_calendar(calendar_id)` - 删除日历
- `create_calendar(calendar)` - 创建日历
- `get_calendar_details(calendar_id)` - 获取日历详情
- `update_calendar(calendar_id, calendar)` - 更新日历

### 已实现的工具函数

| 工具名称 | 功能 | 状态 |
|---------|------|------|
| `list_events` | 查询指定时间范围内的事件 | ✅ 已实现 |
| `create_event` | 创建新事件 | ✅ 已实现 |
| `update_event` | 更新现有事件 | ✅ 已实现 |
| `delete_event` | 删除指定事件 | ✅ 已实现 |
| `get_event` | 获取事件详情 | ✅ 已实现 |
| `list_calendars` | 列出用户所有日历 | ✅ 已实现 |
| `clear_calendar` | 清空日历中的所有事件 | ✅ 已实现 |
| `delete_calendar` | 删除指定日历 | ✅ 已实现 |
| `create_calendar` | 创建新日历 | ✅ 已实现 |
| `get_calendar_details` | 获取日历详情 | ✅ 已实现 |
| `update_calendar` | 更新日历信息 | ✅ 已实现 |
| `list_recurring_events` | 查询重复事件列表 | ✅ 已实现 |
| `create_recurring_event` | 创建重复事件 | ✅ 已实现 |
| `update_recurring_event` | 更新重复事件 | ✅ 已实现 |
| `delete_recurring_event` | 删除重复事件 | ✅ 已实现 |
| `get_recurring_event_instances` | 获取重复事件的所有实例 | ✅ 已实现 |

### 重复事件(RRULE)使用说明

#### 重复规则格式

重复规则使用iCalendar RRULE格式，格式为：`FREQ=<频率>;<其他参数>`

**频率(FREQ)选项:**
- `DAILY` - 每天
- `WEEKLY` - 每周
- `MONTHLY` - 每月
- `YEARLY` - 每年

**常用参数:**
- `COUNT=数字` - 重复次数
- `UNTIL=日期` - 重复结束日期(格式：YYYYMMDD)
- `INTERVAL=数字` - 间隔(默认为1，如INTERVAL=2表示每两周)
- `BYDAY=MO,TU,WE,TH,FR,SA,SU` - 指定星期几(每周时使用)
- `BYMONTHDAY=数字` - 指定每月第几天(每月时使用)
- `BYMONTH=数字` - 指定月份(每年时使用)

#### 常用重复规则示例

```python
# 每天重复10次
"FREQ=DAILY;COUNT=10"

# 每周一、三、五重复
"FREQ=WEEKLY;BYDAY=MO,WE,FR"

# 每周一重复
"FREQ=WEEKLY;BYDAY=MO"

# 每两周重复一次
"FREQ=WEEKLY;INTERVAL=2"

# 每月15日重复
"FREQ=MONTHLY;BYMONTHDAY=15"

# 每月第一个周一
"FREQ=MONTHLY;BYDAY=1MO"

# 每年12月25日重复
"FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25"

# 每年1月1日重复
"FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1"

# 每天重复，直到2024年12月31日
"FREQ=DAILY;UNTIL=20241231"

# 每周一到周五重复，重复20次
"FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;COUNT=20"
```

#### 更新/删除范围说明

**update_scope / delete_scope 参数:**

| 范围 | 说明 | 示例 |
|-----|------|------|
| `single` | 只更新/删除此实例 | 只修改这次会议，不影响后续会议 |
| `future` | 更新/删除此实例及所有未来实例 | 从这次会议开始，所有后续会议都修改 |
| `all` | 更新/删除所有实例 | 包括过去和未来的所有会议 |

**使用场景示例:**

```python
# 场景1: 只取消今天的一次团队会议
delete_recurring_event(
    provider="google",
    event_id="event_id",
    calendar_id="primary",
    delete_scope="single"
)

# 场景2: 从今天开始，把团队会议时间从10点改到14点
update_recurring_event(
    provider="google",
    event_id="event_id",
    calendar_id="primary",
    start_time="2024-03-11T14:00:00",
    end_time="2024-03-11T15:00:00",
    update_scope="future"
)

# 场景3: 完全取消整个重复会议系列
delete_recurring_event(
    provider="google",
    event_id="event_id",
    calendar_id="primary",
    delete_scope="all"
)
```

### Google Calendar API v3 完整工具列表

#### 1. Events (事件)
**功能**: 管理日历中的事件

- **watch**: 监视日历中的变更，通过推送通知接收更新
- **list**: 列出指定日历中的事件（支持 `singleEvents=false` 查询重复事件）
- **get**: 获取单个事件的详细信息
- **insert**: 创建新事件（支持通过 `recurrence` 参数创建重复事件）
- **update**: 更新现有事件（必须提供event ID）
- **patch**: 部分更新事件（只更新提供的字段）
- **delete**: 删除事件（支持通过originalStart参数删除重复事件实例）
- **instances**: 获取重复事件的实例列表（查看重复事件的所有具体实例）
- **import**: 从其他日历导入事件
- **quickAdd**: 快速创建事件（使用文本解析）
- **move**: 将事件移动到其他日历

**重复事件相关说明**:
- 在 `insert` 时设置 `recurrence` 参数（RRULE格式）可创建重复事件
- 在 `list` 时设置 `singleEvents=false` 可查询重复事件本身
- 在 `update`/`delete` 时，通过 `recurringEventId` 和 `originalStart` 参数控制更新/删除范围
  - 只提供event ID: 只更新/删除单个实例
  - 提供recurringEventId和originalStart: 从指定实例开始更新/删除未来所有实例
  - 提供recurringEventId但不提供originalStart: 更新/删除所有实例（包括过去）
- 使用 `instances` 方法可以查看重复事件的所有具体实例

#### 2. CalendarList (日历列表)
**功能**: 管理用户的日历列表（订阅和属性设置）

- **list**: 列出用户日历列表中的所有日历
- **get**: 获取日历列表中某个日历的元数据
- **insert**: 将现有日历添加到用户的日历列表中
- **update**: 更新日历列表中日历的属性（如颜色、通知等）
- **patch**: 部分更新日历列表中的日历属性
- **delete**: 从用户日历列表中移除日历（不删除日历本身）

#### 3. Calendars (日历)
**功能**: 管理日历本身（创建、删除和基本属性）

- **get**: 获取日历的元数据
- **insert**: 创建新的次要日历
- **update**: 更新日历的元数据
- **delete**: 永久删除日历及其所有事件
- **clear**: 清空日历中的所有主要事件

#### 4. Acl (访问控制列表)
**功能**: 管理日历的共享权限

- **list**: 列出日历的访问控制规则
- **get**: 获取特定的访问控制规则
- **insert**: 添加新的访问控制规则（共享日历）
- **update**: 更新访问控制规则
- **patch**: 部分更新访问控制规则
- **delete**: 删除访问控制规则

#### 5. Freebusy (空闲/忙碌)
**功能**: 查询多个日历的空闲/忙碌状态

- **query**: 查询指定日历和时间段内的空闲/忙碌时间

#### 6. Colors (颜色)
**功能**: 获取日历和事件的颜色定义

- **get**: 获取日历和事件的可用颜色列表

#### 7. Settings (设置)
**功能**: 管理用户的日历设置

- **list**: 列出用户的所有日历设置
- **get**: 获取特定设置的值

#### 8. Channels (通道)
**功能**: 管理推送通知通道

- **stop**: 停止监视资源的通道

### Google Calendar API 说明

#### 日历和日历列表的区别

| 特性 | Calendars | CalendarList |
|-----|-----------|--------------|
| **含义** | 实际的日历对象（包含事件） | 用户订阅/关注的日历列表 |
| **创建** | 可以创建新的次要日历 | 只能将已有日历添加到列表 |
| **删除** | 删除日历和所有事件（永久删除） | 只是从列表中移除，日历仍然存在 |
| **用途** | 管理日历的生命周期 | 控制日历在用户界面的显示和属性 |
| **包含内容** | 事件、ACL、日历属性 | 显示名称、颜色、通知设置等 |
| **对应关系** | 一个Calendar可以被多个用户添加到自己的CalendarList | 一个用户的CalendarList中的每个条目对应一个Calendar |

#### 删除日历与CalendarList的关系

**删除Calendar时**:
- 日历和所有事件被永久删除
- 如果CalendarList中引用此日历，引用会失效
- 无法恢复删除的日历

**删除CalendarList时**:
- 只是从用户的日历列表中移除
- 日历本身和事件仍然存在
- 其他用户如果订阅了此日历，仍然可以看到
- 可以重新通过CalendarList.insert()添加回来

**示例场景**:
- 用户A创建了日历"团队日历"（Calendars）
- 用户B通过CalendarList.add()订阅了"团队日历"
- 用户A删除了"团队日历"（Calendars.delete）
- 用户B的CalendarList中仍然有此日历，但访问时会返回404错误
- 如果只是用户B从CalendarList中删除，用户A和其他订阅者仍然可以访问

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
