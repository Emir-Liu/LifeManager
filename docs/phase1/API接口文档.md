# LifeManager MVP API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

---

## 通用响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 1,
  "message": "错误描述",
  "data": null
}
```

---

## 1. 认证模块

### 1.1 用户注册

**接口**: `POST /api/auth/register`

**请求头**:
```
Content-Type: application/json
```

**请求参数**:
```json
{
  "username": "testuser",
  "password": "password123",
  "email": "test@example.com"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "testuser",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**错误码**:
- `1001`: 用户名已存在
- `1002`: 参数错误

---

### 1.2 用户登录

**接口**: `POST /api/auth/login`

**请求参数**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "username": "testuser",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**错误码**:
- `1003`: 用户不存在
- `1004`: 密码错误

---

## 2. 目标模块

### 2.1 获取目标列表

**接口**: `GET /api/goals`

**请求头**:
```
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "title": "学习 Python 编程",
      "description": "在 3 个月内掌握 Python 基础语法和常用库",
      "deadline": "2025-04-26",
      "status": "planning",
      "created_at": "2025-01-26T10:00:00Z"
    }
  ]
}
```

---

### 2.2 创建目标

**接口**: `POST /api/goals`

**请求参数**:
```json
{
  "title": "学习 Python 编程",
  "description": "在 3 个月内掌握 Python 基础语法和常用库",
  "deadline": "2025-04-26"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "创建成功",
  "data": {
    "id": 1,
    "title": "学习 Python 编程",
    "deadline": "2025-04-26",
    "status": "planning"
  }
}
```

---

### 2.3 获取目标详情

**接口**: `GET /api/goals/:id`

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "title": "学习 Python 编程",
    "description": "...",
    "deadline": "2025-04-26",
    "status": "confirmed",
    "created_at": "2025-01-26T10:00:00Z",
    "tasks_count": 15,
    "completed_tasks": 5
  }
}
```

---

### 2.4 删除目标

**接口**: `DELETE /api/goals/:id`

**响应示例**:
```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

---

## 3. 规划模块（核心）

### 3.1 生成规划 ⭐

**接口**: `POST /api/plans/generate`

**请求参数**:
```json
{
  "goal_id": 1,
  "available_hours_per_day": 2
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "规划生成成功",
  "data": {
    "plan_id": 1,
    "goal_id": 1,
    "content": {
      "stages": [
        {
          "name": "基础语法学习",
          "tasks": [
            {
              "title": "安装 Python 环境",
              "description": "下载并安装 Python 3.10+",
              "estimated_hours": 0.5,
              "order": 1,
              "due_date": "2025-01-27"
            },
            {
              "title": "学习变量和数据类型",
              "description": "理解整数、浮点数、字符串等",
              "estimated_hours": 2,
              "order": 2,
              "due_date": "2025-01-28"
            }
          ]
        },
        {
          "name": "函数和模块",
          "tasks": [...]
        }
      ]
    },
    "total_stages": 3,
    "total_tasks": 15,
    "estimated_total_hours": 30
  }
}
```

---

### 3.2 获取规划详情

**接口**: `GET /api/plans/:id`

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "goal_id": 1,
    "goal_title": "学习 Python 编程",
    "content": {...},
    "status": "draft"
  }
}
```

---

### 3.3 确认规划 ⭐

**接口**: `POST /api/plans/:id/confirm`

**说明**: 确认规划后，系统会自动创建所有任务并安排到日程

**请求参数**:
```json
{
  "content": {...} // 可选：修改后的规划内容
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "规划确认成功，已创建 15 个任务",
  "data": {
    "plan_id": 1,
    "tasks_created": 15
  }
}
```

---

### 3.4 修改规划

**接口**: `PUT /api/plans/:id`

**请求参数**:
```json
{
  "content": {
    "stages": [...]
  }
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "修改成功",
  "data": {
    "id": 1,
    "content": {...}
  }
}
```

---

## 4. 任务模块

### 4.1 获取任务列表

**接口**: `GET /api/tasks`

**查询参数**:
- `goal_id`: 目标 ID（可选）
- `date`: 日期（可选，格式：YYYY-MM-DD）
- `status`: 状态（可选：completed, pending）

**请求示例**:
```
GET /api/tasks?goal_id=1&date=2025-01-27
```

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "goal_id": 1,
      "plan_id": 1,
      "title": "安装 Python 环境",
      "description": "下载并安装 Python 3.10+",
      "due_date": "2025-01-27T10:00:00Z",
      "completed": false,
      "created_at": "2025-01-26T10:00:00Z"
    }
  ]
}
```

---

### 4.2 获取今日任务

**接口**: `GET /api/tasks/today`

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "title": "安装 Python 环境",
      "due_date": "2025-01-27T10:00:00Z",
      "completed": false
    }
  ],
  "total": 5,
  "completed": 2
}
```

---

### 4.3 创建任务

**接口**: `POST /api/tasks`

**请求参数**:
```json
{
  "goal_id": 1,
  "title": "额外添加的任务",
  "description": "手动添加的任务",
  "due_date": "2025-01-27T14:00:00Z"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "创建成功",
  "data": {
    "id": 16,
    "title": "额外添加的任务"
  }
}
```

---

### 4.4 完成任务

**接口**: `PUT /api/tasks/:id/complete`

**响应示例**:
```json
{
  "code": 0,
  "message": "任务已完成",
  "data": {
    "id": 1,
    "completed": true
  }
}
```

---

### 4.5 取消完成任务

**接口**: `PUT /api/tasks/:id/uncomplete`

**响应示例**:
```json
{
  "code": 0,
  "message": "已取消完成状态",
  "data": {
    "id": 1,
    "completed": false
  }
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 1001 | 用户名已存在 |
| 1002 | 参数错误 |
| 1003 | 用户不存在 |
| 1004 | 密码错误 |
| 2001 | 目标不存在 |
| 2002 | 目标不属于当前用户 |
| 3001 | 规划不存在 |
| 3002 | 规划已确认，无法修改 |
| 4001 | 任务不存在 |
| 4002 | AI 服务不可用 |
| 4003 | AI 生成失败 |

---

## 调用示例

### JavaScript (前端)

```javascript
import { post, get } from '@/utils/request.js'

// 生成规划
const generatePlan = async (goalId) => {
  try {
    const result = await post('/plans/generate', {
      goal_id: goalId,
      available_hours_per_day: 2
    })
    return result
  } catch (error) {
    console.error('生成失败:', error)
  }
}

// 确认规划
const confirmPlan = async (planId) => {
  try {
    const result = await post(`/plans/${planId}/confirm`)
    return result
  } catch (error) {
    console.error('确认失败:', error)
  }
}
```

### Python (测试)

```python
import requests

BASE_URL = "http://localhost:8000/api"
token = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 生成规划
response = requests.post(
    f"{BASE_URL}/plans/generate",
    json={"goal_id": 1, "available_hours_per_day": 2},
    headers=headers
)
print(response.json())
```

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-27 | v1.0 | 初始版本，完成 API 文档 |
