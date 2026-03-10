# Google Calendar API v3 完整接口调用代码库

## 📚 项目概述

本项目提供了 Google Calendar API v3 所有核心接口的完整调用代码和详细的中文文档。所有接口都已封装成易于使用的类和方法，支持完整的日历管理功能。

### ✨ 核心特性

- ✅ **完整的API覆盖**: 包含所有核心资源接口（Calendars, Events, CalendarList, Acl, Freebusy, Settings, Channels）
- ✅ **中文注释**: 所有方法和参数都有详细的中文说明
- ✅ **易于使用**: 统一的客户端接口，简单直观的API设计
- ✅ **完整示例**: 20个实际应用场景的完整代码示例
- ✅ **详细文档**: 包含安装指南、使用说明、错误处理等完整文档

---

## 📁 文件结构

```
code_demo/
├── 📄 核心代码
│   ├── config.py                      # 配置文件（常量、权限范围、颜色映射等）
│   ├── base_client.py                 # 基础客户端（OAuth认证、错误处理、日期格式化）
│   ├── google_calendar_client.py      # 统一客户端（整合所有服务）
│   │
├── 📦 服务模块
│   ├── calendars_service.py           # 日历资源服务（创建、读取、更新、删除日历）
│   ├── events_service.py              # 事件资源服务（事件增删改查、移动、导入等）
│   ├── calendarlist_service.py        # 日历列表服务（管理用户可见日历的显示属性）
│   ├── acl_service.py                 # 访问控制服务（管理日历共享和权限）
│   ├── freebusy_service.py            # 忙闲查询服务（查询和计算空闲时间）
│   ├── settings_service.py            # 设置服务（读取用户偏好设置）
│   ├── channels_service.py            # 通道服务（管理Webhook通知）
│   │
├── 📖 文档和示例
│   ├── README.md                      # 详细文档（所有API接口说明）
│   ├── INSTALL.md                     # 安装指南（OAuth配置、依赖安装）
│   ├── examples.py                    # 完整示例（20个实际应用场景）
│   ├── quickstart.py                  # 快速入门（5分钟上手）
│   ├── requirements.txt               # Python依赖包
│   └── INDEX.md                       # 本文件（项目索引）
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 OAuth 凭证

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用 Calendar API
3. 创建 OAuth 2.0 客户端 ID（桌面应用类型）
4. 下载 `client_secret.json` 到项目目录

详细步骤请参考：[INSTALL.md](INSTALL.md)

### 3. 运行快速入门

```bash
python quickstart.py
```

首次运行会自动打开浏览器进行 OAuth 认证。

---

## 📖 文档导航

### 快速入门
- **[quickstart.py](quickstart.py)** - 5分钟快速上手，最简单的使用示例

### 详细文档
- **[README.md](README.md)** - 完整API文档，包含所有接口的详细说明
  - [概述](README.md#概述)
  - [配置说明](README.md#配置说明)
  - [核心服务](README.md#核心服务)
  - [使用示例](README.md#使用示例)
  - [注意事项](README.md#注意事项)
  - [错误处理](README.md#错误处理)
  - [配额管理](README.md#配额管理)

### 安装指南
- **[INSTALL.md](INSTALL.md)** - 详细的安装和配置指南
  - [前置要求](INSTALL.md#前置要求)
  - [安装步骤](INSTALL.md#安装步骤)
  - [常见问题](INSTALL.md#常见问题)

### 完整示例
- **[examples.py](examples.py)** - 20个实际应用场景的完整代码示例
  - 示例1: 创建简单事件
  - 示例2: 创建重复事件
  - 示例3: 创建带参与者的会议
  - 示例4: 查询事件列表
  - 示例5: 搜索事件
  - 示例6: 更新事件
  - 示例7: 删除事件
  - 示例8: 创建日历
  - 示例9: 查询日历列表
  - 示例10: 查询忙闲状态
  - 示例11: 查找共同空闲时间
  - 示例12: 快速创建事件
  - 示例13: 移动事件到其他日历
  - 示例14: 共享日历
  - 示例15: 查询访问控制列表
  - 示例16: 获取用户设置
  - 示例17: 错误处理
  - 示例18: 获取重复事件实例
  - 示例19: 更新日历列表显示属性
  - 示例20: 完整的日历操作流程

---

## 💡 核心服务介绍

### 1. CalendarsService - 日历资源
管理日历本身的元数据（创建、读取、更新、删除日历）

**主要方法**:
- `get()` - 获取日历元数据
- `insert()` - 创建次级日历
- `update()` - 更新日历元数据
- `patch()` - 部分更新日历
- `delete()` - 删除次级日历
- `clear()` - 清空主日历

### 2. EventsService - 事件资源
管理日历中的事件（增删改查、移动、导入等）

**主要方法**:
- `get()` - 获取单个事件
- `list()` - 列出事件
- `insert()` - 创建事件
- `update()` - 更新事件
- `patch()` - 部分更新事件
- `delete()` - 删除事件
- `move()` - 移动事件
- `quickAdd()` - 快速创建事件
- `import_()` - 导入事件
- `instances()` - 获取重复事件实例

### 3. CalendarListService - 日历列表
管理用户可见日历的显示属性（颜色、标题、通知偏好等）

**主要方法**:
- `list()` - 获取日历列表
- `get()` - 获取特定日历
- `insert()` - 插入日历到列表
- `update()` - 更新日历列表
- `patch()` - 部分更新日历列表
- `delete()` - 从列表中移除日历

### 4. AclService - 访问控制
管理日历的访问权限和共享设置

**主要方法**:
- `list()` - 获取ACL列表
- `get()` - 获取ACL规则
- `insert()` - 创建ACL规则
- `update()` - 更新ACL规则
- `patch()` - 部分更新ACL规则
- `delete()` - 删除ACL规则

### 5. FreebusyService - 忙闲查询
查询和计算多个日历的忙闲状态

**主要方法**:
- `query()` - 查询忙闲信息
- `find_free_time()` - 查找共同空闲时间
- `is_busy_at()` - 检查特定时间是否忙碌

### 6. SettingsService - 设置资源
读取用户的日历偏好设置

**主要方法**:
- `list()` - 获取所有设置
- `get()` - 获取单个设置
- `get_timezone()` - 获取时区设置
- `get_locale()` - 获取区域设置
- `get_week_start()` - 获取一周开始日
- `get_default_event_length()` - 获取默认事件长度
- `get_format24_hour_time()` - 获取24小时制设置

### 7. ChannelsService - 通道资源
管理Webhook通知通道

**主要方法**:
- `create_channel()` - 创建通道配置
- `create_stop_config()` - 创建停止配置
- `stop()` - 停止监听通道

---

## 🎯 典型使用场景

### 场景1: 会议管理系统
```python
from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta

client = GoogleCalendarClient()

# 创建带参与者的会议
event = client.events.insert(
    summary='团队周会',
    start=datetime.now() + timedelta(days=1, hours=10),
    end=datetime.now() + timedelta(days=1, hours=11),
    attendees=[
        {'email': 'user1@example.com'},
        {'email': 'user2@example.com'}
    ],
    recurrence=['RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=10'],
    reminders={
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24*60},
            {'method': 'popup', 'minutes': 15}
        ]
    }
)
```

### 场景2: 日历共享系统
```python
# 共享日历给团队成员
rule = client.acl.insert(
    scope_type='user',
    role='writer',
    scope_value='user@example.com',
    send_notifications=True
)
```

### 场景3: 空闲时间查询
```python
# 查找多个日历的共同空闲时间
free_times = client.freebusy.find_free_time(
    time_min=datetime(2025, 3, 10, 9, 0, 0),
    time_max=datetime(2025, 3, 10, 18, 0, 0),
    calendar_ids=['primary', 'user1@example.com'],
    duration_minutes=60
)

for free in free_times:
    print(f"{free['start']} - {free['end']}")
```

---

## ⚙️ 配置说明

### 权限范围 (SCOPES)

| 权限范围 | 说明 |
|---------|------|
| `https://www.googleapis.com/auth/calendar` | 完整的日历访问权限 |
| `https://www.googleapis.com/auth/calendar.readonly` | 只读权限 |
| `https://www.googleapis.com/auth/calendar.events` | 事件访问权限 |
| `https://www.googleapis.com/auth/calendar.settings` | 设置访问权限 |

### 时区设置

在 `config.py` 中修改默认时区：
```python
TIMEZONE = 'Asia/Shanghai'  # 支持IANA时区格式
```

### 颜色映射

内置11种颜色ID，可在 `config.py` 中查看：
```python
COLOR_MAP = {
    '1': '#7986CB',  # 蓝色
    '2': '#33B679',  # 青绿色
    # ... 更多颜色
}
```

---

## ⚠️ 注意事项

### 配额限制
- 每日 API 调用限制：10,000 次
- 每个 `patch` 请求消耗 3 个配额单位
- 建议使用 `get` + `update` 而不是 `patch`

### 错误处理
所有方法都可能抛出异常，建议使用 try-except 捕获：
```python
try:
    event = client.events.get('event_id')
except Exception as e:
    print(f"获取事件失败: {str(e)}")
```

### 时间格式
- 时间格式：RFC3339 格式（如 `2025-03-10T14:00:00+08:00`）
- 日期格式：`YYYY-MM-DD`（如 `2025-03-10`）
- 所有 datetime 对象会自动转换

---

## 📚 参考资料

- [Google Calendar API v3 官方文档](https://developers.google.com/workspace/calendar/api/v3/reference)
- [OAuth 2.0 认证指南](https://developers.google.com/workspace/guides/authenticate-overview)
- [Python 客户端库文档](https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.html)

---

## 📝 更新日志

### v1.0.0 (2025-03-09)
- ✨ 初始版本发布
- ✅ 完整覆盖 Google Calendar API v3 所有核心资源
- ✅ 提供20个完整使用示例
- ✅ 详细的中文文档和注释
- ✅ 统一的客户端接口设计

---

## 📄 许可证

本项目仅供学习和参考使用。

---

## 💬 支持

如有问题，请查阅：
1. [README.md](README.md) - 详细文档
2. [INSTALL.md](INSTALL.md) - 安装指南
3. [examples.py](examples.py) - 完整示例
4. [Google Calendar API 官方文档](https://developers.google.com/workspace/calendar/api/v3/reference)

---

**Happy Coding! 🎉**
