# Google Calendar API v3 接口调用文档

## 目录
- [概述](#概述)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [核心服务](#核心服务)
  - [1. Calendars - 日历资源](#1-calendars---日历资源)
  - [2. Events - 事件资源](#2-events---事件资源)
  - [3. CalendarList - 日历列表资源](#3-calendarlist---日历列表资源)
  - [4. Acl - 访问控制列表资源](#4-acl---访问控制列表资源)
  - [5. Freebusy - 忙闲查询资源](#5-freebusy---忙闲查询资源)
  - [6. Settings - 设置资源](#6-settings---设置资源)
  - [7. Channels - 通道资源](#7-channels---通道资源)
- [使用示例](#使用示例)
- [注意事项](#注意事项)
- [错误处理](#错误处理)
- [配额管理](#配额管理)

---

## 概述

本文档提供了 Google Calendar API v3 所有核心接口的详细调用说明和中文注释。所有代码已经封装成易于使用的类和方法，支持完整的日历管理功能。

### 支持的功能
- ✅ 日历管理（创建、读取、更新、删除）
- ✅ 事件管理（创建、读取、更新、删除、移动、导入）
- ✅ 忙闲查询
- ✅ 访问控制
- ✅ 用户设置
- ✅ 监听/推送通知（Webhook）

---

## 快速开始

### 1. 安装依赖

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2. 获取 OAuth 2.0 凭证

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目或选择现有项目
3. 启用 Calendar API
4. 创建 OAuth 2.0 客户端 ID
5. 下载 `client_secret.json` 文件

### 3. 基本使用

```python
from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta

# 初始化客户端
client = GoogleCalendarClient()

# 创建事件
event = client.events.insert(
    summary='团队会议',
    start=datetime.now(),
    end=datetime.now() + timedelta(hours=1),
    description='讨论项目进度'
)

print(f"事件ID: {event['id']}")
```

---

## 配置说明

### `config.py` 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SCOPES` | OAuth 2.0 权限范围 | 完整日历访问权限 |
| `CLIENT_SECRET_FILE` | OAuth 客户端密钥文件 | `client_secret.json` |
| `CREDENTIALS_FILE` | 存储的凭据文件 | `token.json` |
| `PRIMARY_CALENDAR_ID` | 主日历ID | `primary` |
| `TIMEZONE` | 默认时区 | `Asia/Shanghai` |
| `MAX_RESULTS` | 每次查询最大结果数 | `100` |

### 权限范围说明

| 权限范围 | 说明 |
|---------|------|
| `https://www.googleapis.com/auth/calendar` | 完整的日历访问权限 |
| `https://www.googleapis.com/auth/calendar.readonly` | 只读权限 |
| `https://www.googleapis.com/auth/calendar.events` | 事件访问权限 |
| `https://www.googleapis.com/auth/calendar.settings` | 设置访问权限 |

---

## 核心服务

### 1. Calendars - 日历资源

**功能**: 直接管理日历本身（创建、删除、更新日历元数据）

#### 主要方法

##### `get(calendar_id)` - 获取日历元数据
```python
calendar = client.calendars.get('primary')
print(f"日历标题: {calendar['summary']}")
print(f"时区: {calendar['timeZone']}")
```

##### `insert(summary, description, location, time_zone)` - 创建次级日历
```python
calendar = client.calendars.insert(
    summary='工作日历',
    description='用于工作安排',
    location='北京',
    time_zone='Asia/Shanghai'
)
```

##### `update(calendar_id, **kwargs)` - 更新日历元数据
```python
calendar = client.calendars.update(
    calendar_id='calendar_id',
    summary='更新后的标题',
    description='更新后的描述'
)
```

##### `patch(calendar_id, **kwargs)` - 部分更新日历
```python
calendar = client.calendars.patch(
    calendar_id='calendar_id',
    summary='仅更新标题'
)
```

##### `delete(calendar_id)` - 删除次级日历
```python
client.calendars.delete('calendar_id')
```

##### `clear(calendar_id)` - 清空主日历
```python
client.calendars.clear('primary')  # 仅限主日历
```

---

### 2. Events - 事件资源

**功能**: 管理日历中的事件

#### 主要方法

##### `get(event_id, calendar_id)` - 获取单个事件
```python
event = client.events.get('event_id')
print(f"事件标题: {event['summary']}")
print(f"开始时间: {event['start']['dateTime']}")
```

##### `list(calendar_id, time_min, time_max, q, ...)` - 列出事件
```python
from datetime import datetime, timedelta

events = client.events.list(
    calendar_id='primary',
    time_min=datetime.now(),
    time_max=datetime.now() + timedelta(days=7),
    q='会议'
)

for event in events:
    print(f"{event['summary']}: {event['start']['dateTime']}")
```

##### `insert(summary, start, end, ...)` - 创建事件
```python
event = client.events.insert(
    summary='团队周会',
    start=datetime.now(),
    end=datetime.now() + timedelta(hours=1),
    description='每周例会',
    location='会议室A',
    attendees=[
        {'email': 'user1@example.com'},
        {'email': 'user2@example.com'}
    ],
    recurrence=['RRULE:FREQ=WEEKLY;COUNT=10'],  # 每周重复10次
    reminders={
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24*60},  # 提前1天
            {'method': 'popup', 'minutes': 15}     # 提前15分钟
        ]
    }
)
```

##### `update(event_id, **kwargs)` - 更新整个事件
```python
event = client.events.update(
    event_id='event_id',
    summary='新标题',
    description='新描述',
    start=datetime.now(),
    end=datetime.now() + timedelta(hours=2)
)
```

##### `patch(event_id, **kwargs)` - 部分更新事件
```python
event = client.events.patch(
    event_id='event_id',
    summary='仅更新标题'
)
```

##### `delete(event_id, calendar_id)` - 删除事件
```python
client.events.delete('event_id')
```

##### `move(event_id, destination_calendar_id)` - 移动事件到其他日历
```python
client.events.move(
    event_id='event_id',
    destination_calendar_id='another_calendar_id'
)
```

##### `quick_add(text, calendar_id)` - 快速创建事件
```python
event = client.events.quick_add(
    text='明天下午3点开会',
    calendar_id='primary'
)
```

##### `import_event(calendar_id, **event_body)` - 导入事件
```python
event = client.events.import_event(
    calendar_id='primary',
    summary='导入的事件',
    start={'date': '2025-03-10'},
    end={'date': '2025-03-11'}
)
```

##### `instances(event_id, calendar_id)` - 获取重复事件实例
```python
instances = client.events.instances(
    event_id='recurring_event_id',
    calendar_id='primary'
)
```

---

### 3. CalendarList - 日历列表资源

**功能**: 管理用户可见和可访问的日历列表中的条目（显示设置、颜色、通知偏好等）

#### 主要方法

##### `list(min_access_role, max_results, ...)` - 获取日历列表
```python
calendars = client.calendar_list.list(
    min_access_role='writer',
    max_results=50
)

for cal in calendars:
    print(f"{cal['summary']}: {cal['accessRole']}")
```

##### `get(calendar_id)` - 获取日历列表中的日历
```python
calendar = client.calendar_list.get('calendar_id')
```

##### `insert(calendar_id, **kwargs)` - 插入日历到列表
```python
calendar = client.calendar_list.insert(
    calendar_id='calendar_id',
    summary_override='自定义标题',
    color_id='2',
    selected=True,
    hidden=False
)
```

##### `update(calendar_id, **kwargs)` - 更新日历列表
```python
calendar = client.calendar_list.update(
    calendar_id='calendar_id',
    color_id='3',
    selected=False
)
```

##### `patch(calendar_id, **kwargs)` - 部分更新日历列表
```python
calendar = client.calendar_list.patch(
    calendar_id='calendar_id',
    summary_override='新标题'
)
```

##### `delete(calendar_id)` - 从列表中移除日历
```python
client.calendar_list.delete('calendar_id')
```

---

### 4. Acl - 访问控制列表资源

**功能**: 管理日历的访问控制规则（ACL规则）

#### 主要方法

##### `list(calendar_id, max_results)` - 获取ACL列表
```python
acl_rules = client.acl.list(calendar_id='primary')

for rule in acl_rules:
    scope_type = rule['scope']['type']
    scope_value = rule['scope'].get('value', '')
    role = rule['role']
    print(f"权限: {role} - 范围: {scope_type}({scope_value})")
```

##### `get(rule_id, calendar_id)` - 获取ACL规则
```python
rule = client.acl.get(rule_id='rule_id', calendar_id='primary')
```

##### `insert(scope_type, role, ...)` - 创建ACL规则
```python
rule = client.acl.insert(
    scope_type='user',
    role='writer',
    scope_value='user@example.com',
    send_notifications=True
)
```

##### `update(rule_id, scope_type, role, ...)` - 更新ACL规则
```python
rule = client.acl.update(
    rule_id='rule_id',
    scope_type='user',
    role='owner',
    scope_value='user@example.com'
)
```

##### `patch(rule_id, **kwargs)` - 部分更新ACL规则
```python
rule = client.acl.patch(
    rule_id='rule_id',
    role='writer'
)
```

##### `delete(rule_id, calendar_id)` - 删除ACL规则
```python
client.acl.delete(rule_id='rule_id')
```

---

### 5. Freebusy - 忙闲查询资源

**功能**: 查询一组日历在特定时间段内的"空闲/忙碌"状态信息

#### 主要方法

##### `query(time_min, time_max, calendar_ids)` - 查询忙闲信息
```python
from datetime import datetime, timedelta

result = client.freebusy.query(
    time_min=datetime.now(),
    time_max=datetime.now() + timedelta(days=7),
    calendar_ids=['primary', 'user@example.com']
)

# 检查某个日历的忙碌时间
busy_times = result['calendars']['primary']['busy']
for busy in busy_times:
    print(f"忙碌: {busy['start']} - {busy['end']}")
```

##### `find_free_time(...)` - 查找共同空闲时间
```python
free_times = client.freebusy.find_free_time(
    time_min=datetime.now(),
    time_max=datetime.now() + timedelta(days=7),
    calendar_ids=['primary', 'user@example.com'],
    duration_minutes=60  # 至少1小时的空闲时间
)

for free in free_times:
    print(f"空闲: {free['start']} - {free['end']}")
    print(f"持续时间: {free['duration_minutes']} 分钟")
```

---

### 6. Settings - 设置资源

**功能**: 管理用户的日历偏好设置

#### 主要方法

##### `list(max_results)` - 获取所有设置
```python
settings = client.settings.list()

for setting in settings:
    print(f"{setting['id']}: {setting['value']}")
```

##### `get(setting_id)` - 获取单个设置
```python
setting = client.settings.get('timezone')
print(f"时区: {setting['value']}")
```

##### 便捷方法

```python
# 获取时区
timezone = client.settings.get_timezone()

# 获取区域设置
locale = client.settings.get_locale()

# 获取一周开始日（0=周日, 1=周一）
week_start = client.settings.get_week_start()

# 获取默认事件长度（分钟）
event_length = client.settings.get_default_event_length()

# 获取24小时制设置
format_24h = client.settings.get_format24_hour_time()

# 获取所有设置为字典
all_settings = client.settings.get_all_settings_dict()
```

---

### 7. Channels - 通道资源

**功能**: 管理 Webhook 通知通道

#### 主要方法

##### `create_channel(channel_id, resource_uri, webhook_url)` - 创建通道配置
```python
import uuid

channel_config = ChannelsService.create_channel(
    channel_id=str(uuid.uuid4()),
    resource_uri='https://www.googleapis.com/calendar/v3/calendars/primary/events',
    webhook_url='https://example.com/webhook',
    ttl_minutes=60
)
```

##### `create_stop_config(channel_id, resource_id)` - 创建停止通道配置
```python
stop_config = ChannelsService.create_stop_config(
    channel_id='channel_id',
    resource_id='resource_id'
)
```

##### `stop(body)` - 停止监听通道
```python
client.channels.stop({
    'id': 'channel_id',
    'resourceId': 'resource_id'
})
```

---

## 使用示例

### 示例1: 创建一个带重复规则的会议事件

```python
from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta

client = GoogleCalendarClient()

event = client.events.insert(
    summary='每周团队会议',
    start=datetime(2025, 3, 10, 14, 0, 0),
    end=datetime(2025, 3, 10, 15, 0, 0),
    description='每周团队例会',
    location='会议室A',
    attendees=[
        {'email': 'user1@example.com'},
        {'email': 'user2@example.com'}
    ],
    recurrence=['RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=10'],  # 每周一，重复10次
    reminders={
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24*60},
            {'method': 'popup', 'minutes': 15}
        ]
    }
)

print(f"事件创建成功，ID: {event['id']}")
```

### 示例2: 查询下周所有事件

```python
from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta

client = GoogleCalendarClient()

# 计算下周的时间范围
now = datetime.now()
start_of_week = now - timedelta(days=now.weekday())
end_of_week = start_of_week + timedelta(days=7)

events = client.events.list(
    calendar_id='primary',
    time_min=start_of_week,
    time_max=end_of_week,
    order_by='startTime'
)

print(f"下周共有 {len(events)} 个事件:")
for event in events:
    print(f"- {event['summary']}: {event['start']['dateTime']}")
```

### 示例3: 查找多个日历的共同空闲时间

```python
from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta

client = GoogleCalendarClient()

free_times = client.freebusy.find_free_time(
    time_min=datetime(2025, 3, 10, 9, 0, 0),
    time_max=datetime(2025, 3, 10, 18, 0, 0),
    calendar_ids=['primary', 'user1@example.com', 'user2@example.com'],
    duration_minutes=60
)

print(f"找到 {len(free_times)} 个共同空闲时间段:")
for free in free_times:
    print(f"{free['start']} - {free['end']} ({free['duration_minutes']} 分钟)")
```

### 示例4: 共享日历给团队成员

```python
from google_calendar_client import GoogleCalendarClient

client = GoogleCalendarClient()

# 给用户写入权限
rule = client.acl.insert(
    scope_type='user',
    role='writer',
    scope_value='user@example.com',
    send_notifications=True
)

print(f"已共享日历给用户，规则ID: {rule['id']}")
```

---

## 注意事项

### 1. 配额限制
- 每日 API 调用限制：10,000 次
- 每个 `patch` 请求消耗 3 个配额单位
- 建议使用 `get` + `update` 而不是 `patch`

### 2. 错误处理
所有方法都可能抛出异常，建议使用 try-except 捕获：

```python
try:
    event = client.events.get('event_id')
except Exception as e:
    print(f"获取事件失败: {str(e)}")
```

### 3. 时间格式
- 时间格式：RFC3339 格式（如 `2025-03-10T14:00:00+08:00`）
- 日期格式：`YYYY-MM-DD`（如 `2025-03-10`）
- 所有 datetime 对象会自动转换

### 4. 重复事件
- 使用 RRULE 格式定义重复规则
- 例如：`RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;COUNT=20`

### 5. 权限范围
- 根据实际需求选择最小权限范围
- 生产环境建议使用只读权限：`https://www.googleapis.com/auth/calendar.readonly`

---

## 错误处理

### 常见错误代码

| 错误代码 | 说明 | 解决方法 |
|---------|------|----------|
| 400 | 请求格式错误 | 检查请求参数 |
| 401 | 未授权 | 检查 OAuth 凭证 |
| 403 | 权限不足 | 检查权限范围 |
| 404 | 资源不存在 | 检查资源ID |
| 409 | 冲突 | 资源已存在 |
| 429 | 配额超限 | 减少请求频率 |

### 错误处理示例

```python
from googleapiclient.errors import HttpError

try:
    event = client.events.get('non_existent_id')
except HttpError as error:
    if error.resp.status == 404:
        print("事件不存在")
    elif error.resp.status == 403:
        print("权限不足")
    else:
        print(f"发生错误: {error}")
```

---

## 配额管理

### 查看配额状态

```python
quota_info = client.get_base_client().get_quota_status()
print(quota_info)
```

### 优化建议

1. **使用 `list` 方法时设置合理的 `max_results`**
2. **缓存频繁访问的数据**
3. **批量操作减少请求次数**
4. **优先使用 `update` 而不是 `patch`**
5. **使用 `syncToken` 进行增量同步**

---

## 完整文件列表

| 文件 | 说明 |
|------|------|
| `config.py` | 配置文件（常量定义） |
| `base_client.py` | 基础客户端（认证、错误处理） |
| `calendars_service.py` | 日历资源服务 |
| `events_service.py` | 事件资源服务 |
| `calendarlist_service.py` | 日历列表资源服务 |
| `acl_service.py` | 访问控制列表服务 |
| `freebusy_service.py` | 忙闲查询服务 |
| `settings_service.py` | 设置资源服务 |
| `channels_service.py` | 通道资源服务 |
| `google_calendar_client.py` | 统一客户端（整合所有服务） |
| `README.md` | 本文档 |

---

## 参考资源

- [Google Calendar API v3 官方文档](https://developers.google.com/workspace/calendar/api/v3/reference)
- [OAuth 2.0 认证指南](https://developers.google.com/workspace/guides/authenticate-overview)
- [配额使用指南](https://developers.google.com/workspace/calendar/api/v3/reference#quota)

---

## 更新日志

- **v1.0.0** (2025-03-09): 初始版本，包含所有核心接口
