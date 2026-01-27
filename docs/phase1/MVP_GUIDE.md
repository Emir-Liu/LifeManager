# LifeManager MVP 开发指南

## 🎯 核心价值

**AI 智能规划** - 用户输入目标，AI 自动生成执行规划并安排日程

---

## MVP 功能范围

### 核心功能（必须实现）

| 功能模块 | 说明 | 优先级 |
|---------|------|--------|
| **用户系统** | 注册、登录 | P0 |
| **创建目标** | 输入目标和描述 | P0 |
| **AI 生成规划** | 调用 AI 生成执行步骤 | ⭐ 核心 |
| **查看规划** | 浏览 AI 生成的规划 | P0 |
| **确认规划** | 用户确认后创建任务 | P0 |
| **任务列表** | 查看每日任务 | P0 |
| **完成任务** | 标记任务完成 | P0 |

### 暂不实现的功能

- ❌ 提醒通知（第二阶段）
- ❌ 数据统计（第二阶段）
- ❌ 日历视图（第二阶段）
- ❌ 任务编辑（第二阶段）
- ❌ 多平台支持（第二阶段）

---

## 技术栈

### 前端
- **框架**: Vue 3 + Uni-app
- **开发工具**: HBuilderX
- **状态管理**: Vuex
- **UI 组件**: 自定义组件

### 后端
- **框架**: FastAPI
- **数据库**: SQLite（快速开发）
- **认证**: JWT
- **AI 集成**: OpenAI API / DeepSeek API
- **数据验证**: Pydantic

---

## 核心流程

### 用户使用流程

```
1. 用户注册/登录
    ↓
2. 创建目标
   - 输入：目标名称、描述、期望完成时间
    ↓
3. AI 生成规划
   - 调用 AI API
   - AI 分析目标，生成执行步骤
   - AI 估算每个步骤的时间
    ↓
4. 查看规划
   - 展示 AI 生成的规划
   - 显示每个阶段、每个任务
    ↓
5. 确认/修改规划
   - 用户可以修改规划
   - 用户确认后保存
    ↓
6. 安排任务到日程
   - 根据规划生成任务
   - 自动分配到日期
    ↓
7. 执行任务
   - 用户按日程完成任务
   - 标记完成状态
```

---

## 数据库设计

### 核心表结构

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 目标表
CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline DATE,
    status VARCHAR(20) DEFAULT 'planning', -- planning, confirmed, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 规划表（AI 生成的规划）
CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    content TEXT NOT NULL, -- AI 生成的完整规划内容（JSON）
    status VARCHAR(20) DEFAULT 'draft', -- draft, confirmed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

-- 任务表（从规划中生成）
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    plan_id INTEGER,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);
```

---

## API 接口设计

### 认证接口

| 接口 | 方法 | 路径 |
|------|------|------|
| 注册 | POST | `/api/auth/register` |
| 登录 | POST | `/api/auth/login` |
| 登出 | POST | `/api/auth/logout` |

### 目标接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|
| 获取列表 | GET | `/api/goals` | 当前用户的目标 |
| 创建目标 | POST | `/api/goals` | 创建新目标 |
| 获取详情 | GET | `/api/goals/:id` | 目标详情 |
| 删除目标 | DELETE | `/api/goals/:id` | 删除目标 |

### 规划接口（核心）

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|
| 生成规划 | POST | `/api/plans/generate` | ⭐ 调用 AI 生成 |
| 获取规划 | GET | `/api/plans/:id` | 查看规划详情 |
| 确认规划 | POST | `/api/plans/:id/confirm` | 确认并生成任务 |
| 修改规划 | PUT | `/api/plans/:id` | 修改规划内容 |

### 任务接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|
| 获取列表 | GET | `/api/tasks` | 当前用户的任务 |
| 获取今日任务 | GET | `/api/tasks/today` | 今天的任务 |
| 创建任务 | POST | `/api/tasks` | 手动创建任务 |
| 完成任务 | PUT | `/api/tasks/:id/complete` | 标记完成 |
| 取消完成 | PUT | `/api/tasks/:id/uncomplete` | 取消完成 |

---

## 页面清单

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | pages/index/index | 欢迎页 |
| 登录 | pages/login/login | 用户登录 |
| 注册 | pages/register/register | 用户注册 |
| 目标列表 | pages/goals/goals | 查看所有目标 |
| 创建目标 | pages/goals/create | 创建新目标 |
| 查看规划 | pages/plans/detail | 查看 AI 生成的规划 ⭐ |
| 规划详情 | pages/plans/confirm | 确认/修改规划 ⭐ |
| 任务列表 | pages/tasks/list | 查看今日任务 |
| 任务详情 | pages/tasks/detail | 任务详情 |

---

## AI 规划提示词设计

### Prompt 模板

```python
prompt = f"""
你是一个专业的目标规划助手。请根据用户的目标，生成一个详细的执行规划。

目标信息：
- 目标名称：{goal.title}
- 目标描述：{goal.description}
- 期望完成时间：{goal.deadline}
- 可用时间：每天约 {available_hours} 小时

要求：
1. 将目标分解为具体的阶段和任务
2. 估算每个任务的预估时间
3. 按照时间顺序安排任务
4. 考虑任务的依赖关系
5. 提供清晰的里程碑

请以 JSON 格式返回规划：
{{
  "stages": [
    {{
      "name": "阶段名称",
      "tasks": [
        {{
          "title": "任务标题",
          "description": "任务描述",
          "estimated_hours": 2,
          "order": 1
        }}
      ]
    }}
  ]
}}
"""
```

---

## 快速开始

### 前端开发

```bash
# 使用 HBuilderX 打开项目
# 项目路径: e:/project/LifeManager/frontend

# 运行到浏览器
# 运行 → 运行到浏览器 → Chrome

# 运行到安卓手机
# 运行 → 运行到手机或模拟器 → Android App 基座
```

### 后端开发

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
# OPENAI_API_KEY=sk-xxx
# DATABASE_URL=sqlite:///./lifemanager.db

# 启动开发服务器
python main.py

# 访问 API 文档
# http://localhost:8000/docs
```

---

## 开发进度

- [x] 前后端框架搭建
- [x] 用户登录注册
- [x] 目标管理
- [ ] AI 规划生成 ⭐ 核心功能
- [ ] 规划确认流程
- [ ] 任务管理

---

## 下一步

1. 实现 AI 规划生成接口
2. 实现规划查看和确认页面
3. 实现任务自动创建
4. 完善任务列表和完成功能
