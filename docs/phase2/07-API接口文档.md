# LifeManager Phase 2 API 接口文档

---

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| **版本** | v1.0 |
| **创建日期** | 2026-03-02 |
| **作者** | 后端开发工程师 |
| **状态** | 草稿 |
| **关联文档** | Phase 2 产品需求文档、Phase 2 数据模型设计文档 |

---

## 2. 目录

- [通用说明](#3-通用说明)
  - [认证方式](#31-认证方式)
  - [请求格式](#32-请求格式)
  - [响应格式](#33-响应格式)
  - [错误码](#34-错误码)
  - [分页参数](#35-分页参数)
- [对话层 API](#4-对话层-api)
  - [对话会话管理](#41-对话会话管理)
  - [对话消息管理](#42-对话消息管理)
  - [对话操作管理](#43-对话操作管理)
- [业务层 API](#5-业务层-api)
  - [目标管理](#51-目标管理)
  - [任务管理](#52-任务管理)
  - [日程管理](#53-日程管理)
- [偏好层 API](#6-偏好层-api)
  - [时间偏好管理](#61-时间偏好管理)

---

## 3. 通用说明

### 3.1 认证方式

所有 API 请求需要在 Header 中携带认证 Token：

```
Authorization: Bearer <access_token>
```

### 3.2 请求格式

**Content-Type**: `application/json`

### 3.3 响应格式

所有 API 统一返回以下格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": 1709366400000
}
```

### 3.4 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
| 1001 | 参数错误 |
| 1002 | 数据验证失败 |
| 1003 | 时间冲突 |
| 1004 | 对话不存在 |

### 3.5 分页参数

```json
{
  "page": 1,
  "page_size": 20
}
```

---

## 4. 对话层 API

### 4.1 对话会话管理

#### 4.1.1 创建对话会话

```http
POST /api/conversations
```

**请求体**：

```json
{
  "title": "学习 Python 目标规划",
  "conversation_type": "goal_planning",
  "related_goal_id": null,
  "related_plan_id": null
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "title": "学习 Python 目标规划",
    "conversation_type": "goal_planning",
    "status": "active",
    "message_count": 0,
    "created_at": "2026-03-02T10:00:00Z"
  }
}
```

**conversation_type 可选值**：
- `goal_planning` - 目标规划
- `schedule_planning` - 日程规划
- `task_adjustment` - 任务调整
- `general_chat` - 通用聊天

---

#### 4.1.2 获取对话会话列表

```http
GET /api/conversations?status=active&page=1&page_size=20
```

**查询参数**：
- `status` (可选): 筛选状态 `active/completed/cancelled`
- `page`: 页码
- `page_size`: 每页数量

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "学习 Python 目标规划",
        "conversation_type": "goal_planning",
        "status": "active",
        "message_count": 5,
        "created_at": "2026-03-02T10:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

---

#### 4.1.3 获取对话会话详情

```http
GET /api/conversations/{conversation_id}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "title": "学习 Python 目标规划",
    "conversation_type": "goal_planning",
    "status": "active",
    "related_goal_id": null,
    "related_plan_id": null,
    "context_summary": "用户希望学习Python，目标是在3个月内掌握基础...",
    "message_count": 5,
    "created_at": "2026-03-02T10:00:00Z",
    "updated_at": "2026-03-02T11:00:00Z"
  }
}
```

---

#### 4.1.4 更新对话会话

```http
PUT /api/conversations/{conversation_id}
```

**请求体**：

```json
{
  "title": "Python 进阶学习规划",
  "status": "completed",
  "context_summary": "已确认学习计划，包含5个主要阶段..."
}
```

---

#### 4.1.5 删除对话会话

```http
DELETE /api/conversations/{conversation_id}
```

---

### 4.2 对话消息管理

#### 4.2.1 发送消息

```http
POST /api/conversations/{conversation_id}/messages
```

**请求体**：

```json
{
  "role": "user",
  "message_type": "text",
  "content": "我想在3个月内学会Python",
  "content_json": null
}
```

**role 可选值**：
- `user` - 用户
- `assistant` - AI助手
- `system` - 系统

**message_type 可选值**：
- `text` - 文本
- `image` - 图片
- `code` - 代码
- `action_request` - 操作请求

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "conversation_id": 1,
    "sequence": 1,
    "role": "user",
    "message_type": "text",
    "content": "我想在3个月内学会Python",
    "created_at": "2026-03-02T10:05:00Z"
  }
}
```

---

#### 4.2.2 获取对话消息列表

```http
GET /api/conversations/{conversation_id}/messages?page=1&page_size=50
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "sequence": 1,
        "role": "user",
        "message_type": "text",
        "content": "我想在3个月内学会Python",
        "created_at": "2026-03-02T10:05:00Z"
      },
      {
        "id": 2,
        "sequence": 2,
        "role": "assistant",
        "message_type": "text",
        "content": "很好的目标！为了在3个月内掌握Python，我建议...",
        "model_used": "gpt-4",
        "tokens_used": 150,
        "created_at": "2026-03-02T10:05:05Z"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 50
  }
}
```

---

#### 4.2.3 AI 对话（非流式）

```http
POST /api/conversations/{conversation_id}/chat
```

**请求体**：

```json
{
  "message": "帮我规划一下学习路径"
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_message": {
      "id": 1,
      "conversation_id": 1,
      "role": "user",
      "message_type": "text",
      "content": "帮我规划一下学习路径",
      "created_at": "2026-03-06T10:05:00Z"
    },
    "ai_message": {
      "id": 2,
      "conversation_id": 1,
      "role": "assistant",
      "message_type": "text",
      "content": "好的！让我帮你规划一下学习路径...",
      "created_at": "2026-03-06T10:05:05Z"
    }
  }
}
```

---

#### 4.2.4 AI 对话（流式）

```http
POST /api/conversations/{conversation_id}/chat/stream
```

**请求体**：

```json
{
  "message": "帮我规划一下学习路径"
}
```

**响应** (Server-Sent Events):

```
event: user_message
data: {"id": 1, "conversation_id": 1, "role": "user", "message_type": "text", "content": "帮我规划一下学习路径", "created_at": "2026-03-06T10:05:00Z"}

event: ai_chunk
data: {"content": "好的"}

event: ai_chunk
data: {"content": "！让我"}

event: ai_chunk
data: {"content": "帮你规划"}

event: ai_chunk
data: {"content": "一下"}

event: ai_complete
data: {"id": 2, "conversation_id": 1, "role": "assistant", "message_type": "text", "content": "好的！让我帮你规划一下学习路径...", "created_at": "2026-03-06T10:05:05Z"}
```

**事件类型**：
- `user_message` - 用户消息（后端保存后返回）
- `ai_chunk` - AI 回复片段（流式输出）
- `ai_complete` - AI 回复完成（完整消息）
- `error` - 错误信息

---

#### 4.2.5 提供用户反馈

```http
POST /api/conversation-messages/{message_id}/feedback
```

**请求体**：

```json
{
  "feedback": "like"
}
```

**feedback 可选值**：
- `like` - 点赞
- `dislike` - 点踩
- `neutral` - 中性

---

### 4.3 对话操作管理

#### 4.3.1 创建操作

```http
POST /api/conversations/{conversation_id}/actions
```

**请求体**：

```json
{
  "message_id": 2,
  "action_type": "create_goal",
  "description": "创建学习Python目标",
  "action_data": {
    "goal": {
      "title": "学习Python",
      "description": "在3个月内掌握Python基础",
      "deadline": "2026-06-30",
      "priority": "high"
    }
  }
}
```

**action_type 可选值**：
- `create_goal` - 创建目标
- `create_task` - 创建任务
- `update_task` - 更新任务
- `delete_task` - 删除任务
- `create_event` - 创建日程
- `update_event` - 更新日程
- `delete_event` - 删除日程

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "message_id": 2,
    "conversation_id": 1,
    "action_type": "create_goal",
    "status": "pending",
    "description": "创建学习Python目标",
    "target_id": null,
    "created_at": "2026-03-02T10:10:00Z"
  }
}
```

---

#### 4.3.2 执行操作

```http
POST /api/conversation-actions/{action_id}/execute
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "status": "executed",
    "target_type": "goal",
    "target_id": 5,
    "result_message": "目标创建成功",
    "executed_at": "2026-03-02T10:10:05Z"
  }
}
```

---

#### 4.3.3 获取操作列表

```http
GET /api/conversations/{conversation_id}/actions?status=pending
```

---

## 5. 业务层 API

### 5.1 目标管理

#### 5.1.1 创建目标（带对话）

```http
POST /api/goals
```

**请求体**：

```json
{
  "title": "学习Python",
  "description": "在3个月内掌握Python基础",
  "deadline": "2026-06-30",
  "priority": "high",
  "parent_id": null,
  "conversation_id": 1
}
```

---

### 5.2 任务管理

#### 5.2.1 创建任务

```http
POST /api/tasks
```

**请求体**：

```json
{
  "goal_id": 5,
  "title": "学习Python基础语法",
  "description": "掌握变量、数据类型、控制流等基础",
  "due_date": "2026-03-15",
  "task_type": "learning",
  "estimated_hours": 10,
  "start_time": "09:00",
  "end_time": "11:00",
  "parent_task_id": null,
  "reminder_enabled": true,
  "reminder_minutes_before": 30
}
```

---

#### 5.2.2 智能分配任务时间

```http
POST /api/tasks/smart-assign
```

**请求体**：

```json
{
  "goal_id": 5,
  "task_ids": [1, 2, 3],
  "date_range": {
    "start_date": "2026-03-05",
    "end_date": "2026-03-20"
  },
  "preferences": {
    "preferred_time": "09:00-18:00",
    "exclude_days": ["Saturday", "Sunday"]
  }
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "assignments": [
      {
        "task_id": 1,
        "assigned_date": "2026-03-05",
        "start_time": "09:00",
        "end_time": "11:00",
        "conflicts": []
      },
      {
        "task_id": 2,
        "assigned_date": "2026-03-06",
        "start_time": "09:00",
        "end_time": "10:30",
        "conflicts": []
      }
    ]
  }
}
```

---

#### 5.2.3 检测时间冲突

```http
POST /api/tasks/detect-conflicts
```

**请求体**：

```json
{
  "task_id": 1,
  "date": "2026-03-05",
  "start_time": "09:00",
  "end_time": "11:00"
}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "has_conflict": true,
    "conflicts": [
      {
        "task_id": 2,
        "title": "团队会议",
        "start_time": "10:00",
        "end_time": "11:30",
        "overlap_minutes": 90
      }
    ]
  }
}
```

---

#### 5.2.4 获取时间线

```http
GET /api/tasks/timeline?date=2026-03-05
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "date": "2026-03-05",
    "tasks": [
      {
        "id": 1,
        "title": "学习Python基础",
        "start_time": "09:00",
        "end_time": "11:00",
        "duration_minutes": 120,
        "status": "not_started",
        "goal_title": "学习Python",
        "task_type": "learning"
      },
      {
        "id": 2,
        "title": "团队会议",
        "start_time": "14:00",
        "end_time": "15:30",
        "duration_minutes": 90,
        "status": "completed",
        "goal_title": null,
        "task_type": "work"
      }
    ],
    "events": []
  }
}
```

---

### 5.3 日程管理

#### 5.3.1 创建日程

```http
POST /api/events
```

**请求体**：

```json
{
  "title": "每周团队会议",
  "description": "项目进度同步会议",
  "event_type": "meeting",
  "start_date": "2026-03-05",
  "end_date": "2026-06-30",
  "start_time": "14:00",
  "end_time": "15:00",
  "recurrence_rules": [
    {
      "rrule": "FREQ=WEEKLY;BYDAY=MO;INTERVAL=1",
      "exdates": ["2026-03-12"],
      "rdates": []
    }
  ],
  "color": "#FF5722"
}
```

---

#### 5.3.2 获取日程列表

```http
GET /api/events?start_date=2026-03-01&end_date=2026-03-31
```

---

#### 5.3.3 更新日程

```http
PUT /api/events/{event_id}
```

---

#### 5.3.4 删除日程

```http
DELETE /api/events/{event_id}
```

---

## 6. 偏好层 API

### 6.1 时间偏好管理

#### 6.1.1 获取时间偏好

```http
GET /api/time-preferences
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "sleep_type": "normal",
    "wake_up_time": "07:00",
    "sleep_time": "23:00",
    "lunch_start": "12:00",
    "lunch_end": "13:30",
    "work_start": "09:00",
    "work_end": "18:00",
    "work_days": "0,1,2,3,4",
    "preferred_task_start": "09:00",
    "preferred_task_end": "18:00",
    "buffer_time_minutes": 10
  }
}
```

---

#### 6.1.2 更新时间偏好

```http
PUT /api/time-preferences
```

**请求体**：

```json
{
  "sleep_type": "normal",
  "wake_up_time": "07:00",
  "sleep_time": "23:00",
  "lunch_start": "12:00",
  "lunch_end": "13:30",
  "work_start": "09:00",
  "work_end": "18:00",
  "work_days": "0,1,2,3,4",
  "preferred_task_start": "09:00",
  "preferred_task_end": "18:00",
  "buffer_time_minutes": 10
}
```

---

#### 6.1.3 获取时间统计

```http
GET /api/time-stats?start_date=2026-03-01&end_date=2026-03-31
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_time_minutes": 3600,
    "by_goal": [
      {
        "goal_id": 5,
        "goal_title": "学习Python",
        "total_minutes": 1800,
        "percentage": 50
      }
    ],
    "by_task_type": [
      {
        "task_type": "learning",
        "total_minutes": 2400,
        "percentage": 66.7
      },
      {
        "task_type": "work",
        "total_minutes": 1200,
        "percentage": 33.3
      }
    ],
    "completion_rate": 0.85
  }
}
```

---

## 7. 管理员 API

### 7.1 权限说明

所有管理员 API 需要管理员权限（`role = admin`），普通用户访问将返回 403 错误。

---

### 7.2 对话管理

#### 7.2.1 获取所有对话列表

```http
GET /api/admin/conversations
```

**查询参数**：
- `skip` (可选): 跳过记录数，默认 0
- `limit` (可选): 每页记录数，默认 20，最大 100
- `user_id` (可选): 按用户 ID 筛选
- `conversation_type` (可选): 按对话类型筛选
- `status` (可选): 按状态筛选
- `search` (可选): 搜索对话标题
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 100,
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "title": "学习 Python 目标规划",
        "conversation_type": "goal_planning",
        "status": "active",
        "message_count": 5,
        "created_at": "2026-03-02T10:00:00Z"
      }
    ],
    "skip": 0,
    "limit": 20
  }
}
```

---

#### 7.2.2 获取对话详情

```http
GET /api/admin/conversations/{conversation_id}
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "title": "学习 Python 目标规划",
    "conversation_type": "goal_planning",
    "status": "active",
    "related_goal_id": null,
    "related_plan_id": null,
    "context_summary": "用户希望学习Python...",
    "message_count": 5,
    "created_at": "2026-03-02T10:00:00Z",
    "updated_at": "2026-03-02T11:00:00Z"
  }
}
```

---

#### 7.2.3 获取对话消息列表

```http
GET /api/admin/conversations/{conversation_id}/messages
```

**查询参数**：
- `skip` (可选): 跳过记录数，默认 0
- `limit` (可选): 每页记录数，默认 100，最大 500
- `role` (可选): 按角色筛选（user/assistant）

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 10,
    "items": [
      {
        "id": 1,
        "conversation_id": 1,
        "sequence": 1,
        "role": "user",
        "message_type": "text",
        "content": "我想在3个月内学会Python",
        "created_at": "2026-03-02T10:05:00Z"
      },
      {
        "id": 2,
        "conversation_id": 1,
        "sequence": 2,
        "role": "assistant",
        "message_type": "text",
        "content": "很好的目标！我建议...",
        "model_used": "gpt-4",
        "tokens_used": 150,
        "created_at": "2026-03-02T10:05:05Z"
      }
    ],
    "skip": 0,
    "limit": 100
  }
}
```

---

#### 7.2.4 删除对话

```http
DELETE /api/admin/conversations/{conversation_id}
```

**响应**：

```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

**注意**：删除对话会级联删除所有关联的消息和操作记录。

---

#### 7.2.5 获取用户的所有对话

```http
GET /api/admin/conversations/users/{user_id}/conversations
```

**查询参数**：
- `skip` (可选): 跳过记录数，默认 0
- `limit` (可选): 每页记录数，默认 20，最大 100

---

#### 7.2.6 搜索消息内容

```http
GET /api/admin/conversations/messages/search?keyword=Python
```

**查询参数**：
- `keyword` (必填): 搜索关键词
- `skip` (可选): 跳过记录数，默认 0
- `limit` (可选): 每页记录数，默认 20，最大 100
- `user_id` (可选): 按用户 ID 筛选

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 50,
    "items": [
      {
        "id": 1,
        "conversation_id": 1,
        "sequence": 1,
        "role": "user",
        "message_type": "text",
        "content": "我想在3个月内学会Python",
        "created_at": "2026-03-02T10:05:00Z"
      }
    ],
    "skip": 0,
    "limit": 20,
    "keyword": "Python"
  }
}
```

---

#### 7.2.7 获取对话统计信息

```http
GET /api/admin/conversations/stats/overview
```

**响应**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_conversations": 100,
    "total_messages": 1000,
    "total_users": 50,
    "active_conversations": 60,
    "conversations_by_type": {
      "goal_planning": 30,
      "schedule_planning": 25,
      "task_adjustment": 20,
      "general_chat": 25
    },
    "conversations_by_status": {
      "active": 60,
      "completed": 35,
      "cancelled": 5
    }
  }
}
```

---

**文档结束**
