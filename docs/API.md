# LifeManager API 接口文档

## 基础信息

- **Base URL**: `https://api.lifemanager.com/v1`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

## 状态码说明

| Code | 说明 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 1. 用户模块

### 1.1 发送验证码
- **POST** `/auth/send-code`
- **描述**: 发送手机验证码

**请求参数**:
```json
{
  "phone": "13800138000"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "expire_time": 300
  }
}
```

### 1.2 用户注册
- **POST** `/auth/register`
- **描述**: 手机号注册

**请求参数**:
```json
{
  "phone": "13800138000",
  "code": "123456",
  "password": "password123",
  "nickname": "用户昵称"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 1.3 用户登录
- **POST** `/auth/login`
- **描述**: 密码登录

**请求参数**:
```json
{
  "phone": "13800138000",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 1.4 刷新Token
- **POST** `/auth/refresh`
- **描述**: 使用refresh_token刷新访问令牌

**请求参数**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "刷新成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 1.5 获取用户信息
- **GET** `/users/me`
- **描述**: 获取当前用户信息
- **认证**: 需要Token

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "phone": "13800138000",
    "nickname": "用户昵称",
    "avatar_url": "https://example.com/avatar.jpg",
    "created_at": "2026-01-23T00:00:00Z"
  }
}
```

### 1.6 更新用户信息
- **PUT** `/users/me`
- **描述**: 更新当前用户信息
- **认证**: 需要Token

**请求参数**:
```json
{
  "nickname": "新昵称",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "phone": "13800138000",
    "nickname": "新昵称",
    "avatar_url": "https://example.com/new-avatar.jpg"
  }
}
```

### 1.7 更新FCM Token
- **PUT** `/users/fcm-token`
- **描述**: 更新推送Token
- **认证**: 需要Token

**请求参数**:
```json
{
  "fcm_token": "fcm_token_string"
}
```

---

## 2. 目标模块

### 2.1 创建目标
- **POST** `/goals`
- **描述**: 创建新目标
- **认证**: 需要Token

**请求参数**:
```json
{
  "title": "学习Python",
  "description": "在3个月内掌握Python基础和进阶知识",
  "target_date": "2026-04-23",
  "priority": 2
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "目标创建成功",
  "data": {
    "id": 1,
    "title": "学习Python",
    "description": "在3个月内掌握Python基础和进阶知识",
    "target_date": "2026-04-23",
    "priority": 2,
    "status": "planning",
    "progress": 0,
    "created_at": "2026-01-23T00:00:00Z"
  }
}
```

### 2.2 获取目标列表
- **GET** `/goals`
- **描述**: 获取用户的所有目标
- **认证**: 需要Token

**查询参数**:
- `status`: 目标状态过滤 (planning, ongoing, completed, paused)
- `page`: 页码，默认1
- `page_size`: 每页数量，默认20

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "title": "学习Python",
        "description": "在3个月内掌握Python基础和进阶知识",
        "target_date": "2026-04-23",
        "priority": 2,
        "status": "ongoing",
        "progress": 30,
        "created_at": "2026-01-23T00:00:00Z"
      }
    ]
  }
}
```

### 2.3 获取目标详情
- **GET** `/goals/{goal_id}`
- **描述**: 获取指定目标的详细信息
- **认证**: 需要Token

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "学习Python",
    "description": "在3个月内掌握Python基础和进阶知识",
    "target_date": "2026-04-23",
    "priority": 2,
    "status": "ongoing",
    "progress": 30,
    "total_tasks": 20,
    "completed_tasks": 6,
    "created_at": "2026-01-23T00:00:00Z",
    "updated_at": "2026-01-25T00:00:00Z"
  }
}
```

### 2.4 更新目标
- **PUT** `/goals/{goal_id}`
- **描述**: 更新目标信息
- **认证**: 需要Token

**请求参数**:
```json
{
  "title": "深入学习Python",
  "description": "更新后的描述",
  "target_date": "2026-05-01",
  "priority": 2,
  "status": "ongoing"
}
```

### 2.5 删除目标
- **DELETE** `/goals/{goal_id}`
- **描述**: 删除目标
- **认证**: 需要Token

**响应示例**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## 3. 规划模块

### 3.1 生成规划
- **POST** `/plans/generate`
- **描述**: 为目标生成智能规划
- **认证**: 需要Token

**请求参数**:
```json
{
  "goal_id": 1,
  "user_preference": "每天学习2小时，周末可以学习4小时"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "规划生成成功",
  "data": {
    "plan_id": 1,
    "title": "Python学习计划",
    "description": "分阶段学习Python，包括基础语法、Web开发、数据分析等",
    "estimated_hours": 60,
    "stages": [
      {
        "stage": 1,
        "title": "Python基础",
        "tasks": [
          {
            "title": "学习Python变量和数据类型",
            "estimated_hours": 4,
            "description": "掌握整数、浮点数、字符串、列表等数据类型"
          }
        ]
      }
    ]
  }
}
```

### 3.2 确认规划
- **POST** `/plans/{plan_id}/confirm`
- **描述**: 确认规划并创建任务
- **认证**: 需要Token

**请求参数**:
```json
{
  "start_date": "2026-01-26",
  "daily_hours": 2,
  "weekend_hours": 4
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "规划已确认，任务已创建",
  "data": {
    "total_tasks": 20,
    "first_task_date": "2026-01-26"
  }
}
```

### 3.3 获取规划列表
- **GET** `/plans`
- **描述**: 获取用户的所有规划
- **认证**: 需要Token

**查询参数**:
- `goal_id`: 目标ID过滤

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "items": [
      {
        "id": 1,
        "goal_id": 1,
        "title": "Python学习计划",
        "estimated_hours": 60,
        "created_at": "2026-01-23T00:00:00Z"
      }
    ]
  }
}
```

### 3.4 获取规划详情
- **GET** `/plans/{plan_id}`
- **描述**: 获取规划详情
- **认证**: 需要Token

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "goal_id": 1,
    "title": "Python学习计划",
    "description": "分阶段学习Python",
    "estimated_hours": 60,
    "stages": [
      {
        "stage": 1,
        "title": "Python基础",
        "tasks": [
          {
            "title": "学习Python变量和数据类型",
            "estimated_hours": 4
          }
        ]
      }
    ]
  }
}
```

---

## 4. 任务模块

### 4.1 创建任务
- **POST** `/tasks`
- **描述**: 创建新任务
- **认证**: 需要Token

**请求参数**:
```json
{
  "goal_id": 1,
  "plan_id": 1,
  "title": "完成第一章练习",
  "description": "完成变量和数据类型的练习题",
  "scheduled_date": "2026-01-26",
  "scheduled_time": "19:00",
  "duration_minutes": 60,
  "priority": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "任务创建成功",
  "data": {
    "id": 1,
    "goal_id": 1,
    "plan_id": 1,
    "title": "完成第一章练习",
    "scheduled_date": "2026-01-26",
    "scheduled_time": "19:00",
    "duration_minutes": 60,
    "priority": 1,
    "status": "pending"
  }
}
```

### 4.2 获取任务列表
- **GET** `/tasks`
- **描述**: 获取任务列表
- **认证**: 需要Token

**查询参数**:
- `date`: 日期筛选 (格式: 2026-01-26)
- `status`: 状态筛选 (pending, in_progress, completed, skipped)
- `goal_id`: 目标ID筛选
- `page`: 页码
- `page_size`: 每页数量

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 15,
    "items": [
      {
        "id": 1,
        "goal_id": 1,
        "title": "完成第一章练习",
        "scheduled_date": "2026-01-26",
        "scheduled_time": "19:00",
        "duration_minutes": 60,
        "priority": 1,
        "status": "pending"
      }
    ]
  }
}
```

### 4.3 获取今日任务
- **GET** `/tasks/today`
- **描述**: 获取今日所有任务
- **认证**: 需要Token

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "completed": 2,
    "pending": 3,
    "items": [
      {
        "id": 1,
        "goal_id": 1,
        "goal_title": "学习Python",
        "title": "完成第一章练习",
        "scheduled_date": "2026-01-26",
        "scheduled_time": "19:00",
        "duration_minutes": 60,
        "priority": 1,
        "status": "pending"
      }
    ]
  }
}
```

### 4.4 更新任务
- **PUT** `/tasks/{task_id}`
- **描述**: 更新任务信息
- **认证**: 需要Token

**请求参数**:
```json
{
  "scheduled_date": "2026-01-27",
  "scheduled_time": "20:00",
  "priority": 2
}
```

### 4.5 完成任务
- **POST** `/tasks/{task_id}/complete`
- **描述**: 标记任务完成
- **认证**: 需要Token

**请求参数**:
```json
{
  "actual_duration_minutes": 45,
  "notes": "顺利完成"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "任务已完成",
  "data": {
    "task_id": 1,
    "goal_progress": 35
  }
}
```

### 4.6 跳过任务
- **POST** `/tasks/{task_id}/skip`
- **描述**: 跳过任务
- **认证**: 需要Token

**请求参数**:
```json
{
  "reason": "临时有事"
}
```

### 4.7 删除任务
- **DELETE** `/tasks/{task_id}`
- **描述**: 删除任务
- **认证**: 需要Token

---

## 5. 日历模块

### 5.1 获取日历任务
- **GET** `/calendar/tasks`
- **描述**: 获取指定日期范围的任务
- **认证**: 需要Token

**查询参数**:
- `start_date`: 开始日期 (格式: 2026-01-01)
- `end_date`: 结束日期 (格式: 2026-01-31)

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "date": "2026-01-26",
      "tasks": [
        {
          "id": 1,
          "title": "完成第一章练习",
          "time": "19:00",
          "duration": 60,
          "status": "pending",
          "priority": 1
        }
      ]
    }
  ]
}
```

### 5.2 批量更新任务时间
- **PUT** `/calendar/tasks/batch-update`
- **描述**: 批量更新任务时间
- **认证**: 需要Token

**请求参数**:
```json
{
  "updates": [
    {
      "task_id": 1,
      "scheduled_date": "2026-01-27",
      "scheduled_time": "20:00"
    },
    {
      "task_id": 2,
      "scheduled_date": "2026-01-28",
      "scheduled_time": "18:00"
    }
  ]
}
```

---

## 6. 提醒模块

### 6.1 创建提醒
- **POST** `/reminders`
- **描述**: 创建任务提醒
- **认证**: 需要Token

**请求参数**:
```json
{
  "task_id": 1,
  "remind_time": "2026-01-26T18:55:00Z",
  "message": "记得完成Python学习任务哦"
}
```

### 6.2 获取提醒列表
- **GET** `/reminders`
- **描述**: 获取提醒列表
- **认证**: 需要Token

**查询参数**:
- `status`: 状态筛选 (pending, sent, failed)

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "items": [
      {
        "id": 1,
        "task_id": 1,
        "task_title": "完成第一章练习",
        "remind_time": "2026-01-26T18:55:00Z",
        "message": "记得完成Python学习任务哦",
        "status": "pending"
      }
    ]
  }
}
```

### 6.3 更新提醒设置
- **PUT** `/reminders/settings`
- **描述**: 更新全局提醒设置
- **认证**: 需要Token

**请求参数**:
```json
{
  "remind_before_minutes": 5,
  "push_enabled": true,
  "vibration_enabled": true,
  "sound_enabled": true
}
```

---

## 7. 统计模块

### 7.1 获取统计数据
- **GET** `/statistics/overview`
- **描述**: 获取用户统计概览
- **认证**: 需要Token

**查询参数**:
- `period`: 统计周期 (daily, weekly, monthly)

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_goals": 5,
    "completed_goals": 2,
    "ongoing_goals": 2,
    "total_tasks": 50,
    "completed_tasks": 30,
    "total_hours": 25,
    "completion_rate": 0.6
  }
}
```

### 7.2 获取任务统计
- **GET** `/statistics/tasks`
- **描述**: 获取任务完成统计
- **认证**: 需要Token

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "by_date": [
      {
        "date": "2026-01-20",
        "completed": 3,
        "total": 5
      },
      {
        "date": "2026-01-21",
        "completed": 4,
        "total": 6
      }
    ],
    "by_goal": [
      {
        "goal_id": 1,
        "goal_title": "学习Python",
        "completed": 10,
        "total": 20
      }
    ]
  }
}
```

### 7.3 获取目标进度
- **GET** `/statistics/goals/{goal_id}/progress`
- **描述**: 获取目标进度详情
- **认证**: 需要Token

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "goal_id": 1,
    "goal_title": "学习Python",
    "progress": 50,
    "total_tasks": 20,
    "completed_tasks": 10,
    "spent_hours": 12,
    "estimated_remaining_hours": 18,
    "expected_completion_date": "2026-03-15"
  }
}
```

---

## 8. 设置模块

### 8.1 获取用户设置
- **GET** `/settings`
- **描述**: 获取用户设置
- **认证**: 需要Token

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "reminder_settings": {
      "remind_before_minutes": 5,
      "push_enabled": true,
      "vibration_enabled": true,
      "sound_enabled": true
    },
    "calendar_settings": {
      "first_day_of_week": 1,
      "default_view": "week"
    },
    "notification_settings": {
      "quiet_hours_start": "22:00",
      "quiet_hours_end": "08:00"
    }
  }
}
```

### 8.2 更新用户设置
- **PUT** `/settings`
- **描述**: 更新用户设置
- **认证**: 需要Token

**请求参数**:
```json
{
  "reminder_settings": {
    "remind_before_minutes": 10,
    "push_enabled": true
  }
}
```

---

## 9. 反馈模块

### 9.1 提交反馈
- **POST** `/feedback`
- **描述**: 提交用户反馈
- **认证**: 需要Token

**请求参数**:
```json
{
  "type": "bug",
  "title": "应用崩溃",
  "content": "在打开日历时应用崩溃",
  "screenshot_url": "https://example.com/screenshot.jpg"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "反馈已提交",
  "data": {
    "feedback_id": 1
  }
}
```

---

## WebSocket 接口

### 连接地址
- `wss://api.lifemanager.com/ws`
- 认证方式: 在连接URL中携带token，例如 `wss://api.lifemanager.com/ws?token=xxx`

### 消息类型

#### 1. 客户端发送消息

**订阅任务更新**
```json
{
  "type": "subscribe",
  "channel": "tasks"
}
```

**订阅提醒通知**
```json
{
  "type": "subscribe",
  "channel": "reminders"
}
```

#### 2. 服务端推送消息

**任务更新通知**
```json
{
  "type": "task_update",
  "data": {
    "task_id": 1,
    "status": "completed",
    "updated_at": "2026-01-26T19:30:00Z"
  }
}
```

**新提醒通知**
```json
{
  "type": "new_reminder",
  "data": {
    "reminder_id": 1,
    "task_id": 1,
    "task_title": "完成第一章练习",
    "message": "该开始学习啦！",
    "remind_time": "2026-01-26T18:55:00Z"
  }
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数错误 |
| 1002 | 验证码错误或过期 |
| 1003 | 手机号已存在 |
| 1004 | 用户不存在 |
| 1005 | 密码错误 |
| 1006 | Token无效或过期 |
| 2001 | 目标不存在 |
| 2002 | 目标已存在 |
| 3001 | 任务不存在 |
| 3002 | 任务已完成 |
| 4001 | 规划不存在 |
| 5001 | 提醒不存在 |
| 9001 | 服务器内部错误 |
| 9999 | 未知错误 |

---

## 请求示例

### 使用cURL

```bash
# 用户登录
curl -X POST "https://api.lifemanager.com/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "password": "password123"
  }'

# 创建目标
curl -X POST "https://api.lifemanager.com/v1/goals" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "学习Python",
    "description": "在3个月内掌握Python基础",
    "target_date": "2026-04-23",
    "priority": 2
  }'
```

### 使用Axios (JavaScript)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.lifemanager.com/v1',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// 获取今日任务
async function getTodayTasks() {
  const response = await api.get('/tasks/today');
  return response.data;
}

// 完成任务
async function completeTask(taskId, actualDuration, notes) {
  const response = await api.post(`/tasks/${taskId}/complete`, {
    actual_duration_minutes: actualDuration,
    notes: notes
  });
  return response.data;
}
```

---

## 附录

### 数据字典

#### 优先级 (priority)
- 0: 低
- 1: 中
- 2: 高

#### 目标状态 (status)
- planning: 规划中
- ongoing: 进行中
- completed: 已完成
- paused: 已暂停

#### 任务状态 (status)
- pending: 待开始
- in_progress: 进行中
- completed: 已完成
- skipped: 已跳过

#### 提醒状态 (status)
- pending: 待发送
- sent: 已发送
- failed: 发送失败
