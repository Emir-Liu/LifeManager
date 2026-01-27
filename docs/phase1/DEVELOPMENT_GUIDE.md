# LifeManager MVP 开发指南

## 文档信息

- **版本**: v1.0
- **创建日期**: 2026-01-27
- **作者**: 产品经理
- **状态**: 已发布
- **适用阶段**: Phase 1 - MVP

---

## 1. 开发环境准备

### 1.1 前端开发环境

#### 安装 HBuilderX

1. 下载 HBuilderX：https://www.dcloud.io/hbuilderx.html
2. 选择"App 开发版"
3. 解压并运行 HBuilderX

#### 配置项目

```bash
# 1. 使用 HBuilderX 打开项目
文件 → 打开目录 → 选择 e:/project/LifeManager/frontend

# 2. 运行到浏览器
运行 → 运行到浏览器 → Chrome

# 3. 运行到手机
运行 → 运行到手机或模拟器 → Android App 基座
```

### 1.2 后端开发环境

#### Python 环境

```bash
# 确保已安装 Python 3.10+
python --version

# 进入后端目录
cd e:/project/LifeManager/backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 配置环境变量

```bash
# 创建 .env 文件
cd backend
touch .env  # Linux/Mac
# 或者手动创建 .env 文件

# .env 文件内容
DATABASE_URL=sqlite:///./lifemanager.db
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 天
OPENAI_API_BASE=https://api.deepseek.com
OPENAI_API_KEY=sk-xxx
AI_MODEL=deepseek-chat
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7
```

#### 初始化数据库

```bash
# 创建数据库表
python init_db.py
```

#### 启动后端服务

```bash
# 启动开发服务器
python main.py

# 访问 API 文档
http://localhost:8000/docs
```

---

## 2. 后端开发流程

### 2.1 创建数据模型

```python
# backend/app/models/task.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    # ... 其他字段

    # 关系
    goal = relationship("Goal", back_populates="tasks")
```

### 2.2 创建 Pydantic Schema

```python
# backend/app/schemas/task.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

class TaskCreate(TaskBase):
    goal_id: int
    due_date: datetime

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    goal_id: int
    due_date: datetime
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

### 2.3 创建 API 路由

```python
# backend/app/api/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的任务列表"""
    tasks = db.query(Task).join(Goal).filter(Goal.user_id == current_user.id).all()
    return tasks

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建任务"""
    # 验证目标所有权
    goal = db.query(Goal).filter(
        Goal.id == task_data.goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="目标不存在")

    new_task = Task(**task_data.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
```

### 2.4 注册路由

```python
# backend/main.py

from fastapi import FastAPI
from app.api import auth, goals, plans, tasks

app = FastAPI(title="LifeManager API")

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
```

---

## 3. 前端开发流程

### 3.1 创建页面

```vue
<!-- frontend/pages/tasks/list.vue -->

<template>
  <view class="tasks-page">
    <!-- 顶部导航 -->
    <view class="header">
      <text class="title">今日任务</text>
      <view class="filter">
        <text :class="['filter-item', filter === 'today' ? 'active' : '']"
              @tap="setFilter('today')">今日</text>
        <text :class="['filter-item', filter === 'all' ? 'active' : '']"
              @tap="setFilter('all')">全部</text>
      </view>
    </view>

    <!-- 任务列表 -->
    <view class="task-list">
      <view v-for="task in displayTasks" :key="task.id" class="task-card">
        <view class="task-header">
          <text :class="['task-title', { completed: task.completed }]">
            {{ task.title }}
          </text>
          <text class="task-time">{{ formatTime(task.due_date) }}</text>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <l-loading v-if="loading"></l-loading>
  </view>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import LLoading from '@/components/l-loading.vue'

export default {
  components: { LLoading },

  data() {
    return {
      filter: 'today'
    }
  },

  computed: {
    ...mapState('task', ['todayTasks', 'tasks', 'loading']),

    displayTasks() {
      return this.filter === 'today' ? this.todayTasks : this.tasks
    }
  },

  onLoad() {
    this.fetchTasks()
  },

  onPullDownRefresh() {
    this.fetchTasks().finally(() => {
      uni.stopPullDownRefresh()
    })
  },

  methods: {
    ...mapActions('task', ['fetchTodayTasks', 'fetchTasks']),

    setFilter(filter) {
      this.filter = filter
      this.fetchTasks()
    },

    async fetchTasks() {
      if (this.filter === 'today') {
        await this.fetchTodayTasks()
      } else {
        await this.fetchTasks({})
      }
    },

    formatTime(dateStr) {
      const date = new Date(dateStr)
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    }
  }
}
</script>

<style scoped>
.tasks-page {
  min-height: 100vh;
  background: #f9fafb;
}

.header {
  padding: 24rpx 32rpx;
  background: white;
}

.title {
  font-size: 40rpx;
  font-weight: 600;
}

.filter {
  display: flex;
  gap: 32rpx;
  margin-top: 24rpx;
}

.filter-item {
  font-size: 28rpx;
  color: #6b7280;
}

.filter-item.active {
  color: #7c3aed;
  font-weight: 600;
}

.task-list {
  padding: 24rpx 32rpx;
}

.task-card {
  padding: 32rpx;
  background: white;
  border-radius: 24rpx;
  margin-bottom: 24rpx;
}

.task-title {
  font-size: 32rpx;
  font-weight: 500;
}

.task-title.completed {
  text-decoration: line-through;
  color: #9ca3af;
}
</style>
```

### 3.2 创建组件

```vue
<!-- frontend/components/l-loading.vue -->

<template>
  <view v-if="visible" class="l-loading">
    <view class="loading-spinner"></view>
    <text class="loading-text">加载中...</text>
  </view>
</template>

<script>
export default {
  name: 'LLoading',

  props: {
    visible: {
      type: Boolean,
      default: true
    }
  }
}
</script>

<style scoped>
.l-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 0;
}

.loading-spinner {
  width: 64rpx;
  height: 64rpx;
  border: 4rpx solid #e5e7eb;
  border-top-color: #7c3aed;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 24rpx;
  font-size: 28rpx;
  color: #6b7280;
}
</style>
```

---

## 4. 开发规范

### 4.1 命名规范

#### 文件命名

- 页面：小写，多个单词用下划线分隔 → `tasks_list.vue`
- 组件：小写，带 `l-` 前缀 → `l-button.vue`
- API：小写 → `task.js`
- 工具：小写 → `date.js`

#### 变量命名

- 常量：大写下划线 → `API_BASE_URL`
- 变量/函数：小驼峰 → `getUserInfo`
- 类：大驼峰 → `UserService`

### 4.2 代码注释

```python
# ✅ 函数必须有文档字符串
def create_task(task_data: TaskCreate, db: Session) -> Task:
    """
    创建任务

    Args:
        task_data: 任务数据
        db: 数据库会话

    Returns:
        创建的任务对象
    """
    pass

# ✅ 复杂逻辑需要注释
# 计算可用天数，排除周末
available_days = 0
for date in daterange(start_date, end_date):
    if date.weekday() < 5:  # 0-4 表示周一到周五
        available_days += 1
```

### 4.3 Git 提交规范

```bash
# 提交格式
<type>(<scope>): <subject>

# 类型
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试
chore: 构建/工具

# 示例
feat(goal): 添加目标创建功能
fix(auth): 修复登录 Token 过期问题
docs(readme): 更新开发指南
```

---

## 5. 调试技巧

### 5.1 后端调试

```python
# 使用 print 调试
print(f"用户 ID: {user_id}")

# 使用日志
from app.core.logger import logger
logger.info(f"创建任务: {task.title}")
logger.error(f"创建失败: {e}")

# 使用 Python debugger
import pdb; pdb.set_trace()
```

### 5.2 前端调试

```javascript
// 使用 console.log
console.log('目标列表:', goals)

// 使用 Vue DevTools
// 安装浏览器插件后，可以查看组件状态和 Vuex 状态

// 断点调试
// 在 HBuilderX 中设置断点
```

---

## 6. 测试

### 6.1 后端测试

```python
# tests/test_tasks.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/api/tasks",
        json={
            "goal_id": 1,
            "title": "测试任务",
            "due_date": "2026-01-28T09:00:00"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "测试任务"
```

### 6.2 前端测试

```bash
# 使用 HBuilderX 的真机调试功能
# 运行 → 运行到手机或模拟器
```

---

## 7. 部署

### 7.1 后端部署

```bash
# 1. 修改环境变量
# .env
DATABASE_URL=postgresql://user:password@host/dbname

# 2. 安装生产依赖
pip install gunicorn uvicorn

# 3. 启动服务
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 7.2 前端部署

```bash
# 1. 使用 HBuilderX 打包
发行 → App-云打包

# 2. 或使用 Uni-app CLI 打包
npm run build:mp-weixin  # 微信小程序
npm run build:h5         # H5
```

---

## 8. 常见问题

### Q1: 数据库连接失败？

**答**: 检查 `.env` 文件中的 `DATABASE_URL` 是否正确。

### Q2: AI 调用失败？

**答**:
1. 检查 `OPENAI_API_KEY` 是否正确
2. 检查网络连接
3. 检查 API 配额

### Q3: 前端请求跨域？

**答**: 在后端添加 CORS 中间件：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-27 | v1.0 | 初始版本，完成开发指南 |
