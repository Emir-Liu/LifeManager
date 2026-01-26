# LifeManager 开发指南

## 环境准备

### 前端开发环境

#### 1. 安装 Node.js
推荐使用 Node.js 18+ 版本。

下载地址: https://nodejs.org/

验证安装:
```bash
node --version
npm --version
```

#### 2. 安装 HBuilderX (Uni-app 开发工具)
下载地址: https://www.dcloud.io/hbuilderx.html

或使用 Vue CLI + HBuilderX 的方式。

#### 3. 安装依赖
```bash
cd frontend
npm install
```

### 后端开发环境

#### 1. 安装 Python 3.10+
下载地址: https://www.python.org/downloads/

验证安装:
```bash
python --version
pip --version
```

#### 2. 安装 PostgreSQL
下载地址: https://www.postgresql.org/download/

开发环境可以使用 SQLite 作为替代。

#### 3. 安装 Redis
Windows:
- 下载 Redis for Windows: https://github.com/microsoftarchive/redis/releases
- 或使用 WSL 安装: `sudo apt install redis-server`

Linux/Mac:
```bash
sudo apt install redis-server  # Ubuntu/Debian
brew install redis              # Mac
```

#### 4. 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

#### 5. 安装依赖
```bash
pip install -r requirements.txt
```

### Docker 环境 (可选)

使用 Docker 可以快速搭建完整的开发环境。

```bash
docker-compose up -d
```

---

## 前端开发

### 项目结构

```
frontend/
├── pages/                  # 页面
│   ├── index/             # 首页
│   ├── goal/              # 目标相关页面
│   ├── plan/              # 规划相关页面
│   ├── calendar/          # 日历页面
│   ├── task/              # 任务相关页面
│   ├── statistics/        # 统计页面
│   └── profile/           # 个人中心
├── components/            # 组件
│   ├── common/           # 通用组件
│   ├── goal/             # 目标组件
│   └── task/             # 任务组件
├── store/                 # Pinia 状态管理
│   ├── user.js           # 用户状态
│   ├── goal.js           # 目标状态
│   ├── task.js           # 任务状态
│   └── reminder.js       # 提醒状态
├── api/                   # API 封装
│   ├── request.js        # Axios 封装
│   ├── user.js           # 用户 API
│   ├── goal.js           # 目标 API
│   ├── task.js           # 任务 API
│   └── reminder.js       # 提醒 API
├── utils/                 # 工具函数
│   ├── date.js           # 日期处理
│   ├── storage.js        # 本地存储
│   └── validate.js       # 表单验证
├── static/                # 静态资源
│   ├── images/           # 图片
│   └── icons/            # 图标
├── App.vue                # 根组件
├── main.js                # 入口文件
├── manifest.json          # Uni-app 配置
├── pages.json             # 页面配置
└── uni.scss               # 全局样式
```

### 快速开始

#### 1. 配置开发环境

编辑 `api/request.js`，配置 API 基础 URL:

```javascript
const baseURL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000/v1'
  : 'https://api.lifemanager.com/v1';
```

#### 2. 启动开发服务器

使用 HBuilderX 打开项目，点击运行到浏览器或模拟器。

或使用命令行:
```bash
npm run dev:h5
npm run dev:mp-weixin  # 微信小程序
npm run dev:app        # APP
```

### 核心功能开发

#### 1. 用户登录

**store/user.js**
```javascript
import { defineStore } from 'pinia';
import { login, getUserInfo } from '@/api/user';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: null,
  }),
  actions: {
    async login(phone, password) {
      const res = await login({ phone, password });
      this.token = res.data.token;
      uni.setStorageSync('token', res.data.token);
      uni.setStorageSync('refresh_token', res.data.refresh_token);
      await this.fetchUserInfo();
    },
    async fetchUserInfo() {
      const res = await getUserInfo();
      this.userInfo = res.data;
    },
    logout() {
      this.token = '';
      this.userInfo = null;
      uni.removeStorageSync('token');
      uni.removeStorageSync('refresh_token');
    },
  },
});
```

#### 2. 创建目标

**pages/goal/create.vue**
```vue
<template>
  <view class="create-goal">
    <u-form :model="form" :rules="rules" ref="formRef">
      <u-form-item label="目标标题" prop="title">
        <u-input v-model="form.title" placeholder="输入目标标题" />
      </u-form-item>
      <u-form-item label="目标描述" prop="description">
        <u-textarea v-model="form.description" placeholder="详细描述你的目标" />
      </u-form-item>
      <u-form-item label="目标日期" prop="target_date">
        <u-datetime-picker
          v-model="form.target_date"
          mode="date"
        />
      </u-form-item>
      <u-form-item label="优先级" prop="priority">
        <u-radio-group v-model="form.priority">
          <u-radio :value="0">低</u-radio>
          <u-radio :value="1">中</u-radio>
          <u-radio :value="2">高</u-radio>
        </u-radio-group>
      </u-form-item>
    </u-form>
    <u-button @click="handleSubmit" type="primary">创建目标</u-button>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { createGoal } from '@/api/goal';

const form = ref({
  title: '',
  description: '',
  target_date: '',
  priority: 1,
});

const rules = {
  title: [
    { required: true, message: '请输入目标标题', trigger: 'blur' }
  ],
  target_date: [
    { required: true, message: '请选择目标日期', trigger: 'change' }
  ],
};

const handleSubmit = async () => {
  try {
    await createGoal(form.value);
    uni.showToast({ title: '创建成功', icon: 'success' });
    uni.navigateBack();
  } catch (error) {
    uni.showToast({ title: error.message, icon: 'none' });
  }
};
</script>
```

#### 3. 今日任务列表

**pages/index/index.vue**
```vue
<template>
  <view class="home">
    <view class="header">
      <text class="date">{{ currentDate }}</text>
      <text class="greeting">{{ greeting }}</text>
    </view>
    
    <view class="stats">
      <view class="stat-item">
        <text class="stat-value">{{ todayStats.completed }}</text>
        <text class="stat-label">已完成</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ todayStats.pending }}</text>
        <text class="stat-label">待完成</text>
      </view>
    </view>
    
    <view class="task-list">
      <view class="section-title">今日任务</view>
      <view
        v-for="task in todayTasks"
        :key="task.id"
        class="task-item"
        @click="handleTaskClick(task)"
      >
        <view class="task-info">
          <text class="task-title">{{ task.title }}</text>
          <text class="task-time">{{ task.scheduled_time }}</text>
        </view>
        <view class="task-status">
          <u-tag :type="task.status === 'completed' ? 'success' : 'primary'">
            {{ getStatusText(task.status) }}
          </u-tag>
        </view>
      </view>
    </view>
    
    <u-fab @click="handleAddTask" />
  </view>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getTodayTasks } from '@/api/task';
import { formatDate } from '@/utils/date';

const todayTasks = ref([]);
const todayStats = ref({ completed: 0, pending: 0 });

const currentDate = computed(() => formatDate(new Date(), 'YYYY年MM月DD日'));
const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return '早上好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

onMounted(async () => {
  await fetchTodayTasks();
});

const fetchTodayTasks = async () => {
  const res = await getTodayTasks();
  todayTasks.value = res.data.items;
  todayStats.value = {
    completed: res.data.completed,
    pending: res.data.pending,
  };
};

const handleTaskClick = (task) => {
  uni.navigateTo({
    url: `/pages/task/detail?id=${task.id}`
  });
};

const handleAddTask = () => {
  uni.navigateTo({ url: '/pages/task/create' });
};

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待开始',
    'in_progress': '进行中',
    'completed': '已完成',
    'skipped': '已跳过',
  };
  return statusMap[status] || status;
};
</script>
```

### 组件开发指南

#### 1. 创建通用组件

**components/common/TaskCard.vue**
```vue
<template>
  <view class="task-card" @click="$emit('click')">
    <view class="task-left">
      <u-checkbox
        v-model="checked"
        @change="handleCheck"
        shape="circle"
      />
    </view>
    <view class="task-content">
      <text class="task-title">{{ task.title }}</text>
      <view class="task-meta">
        <text class="task-time">{{ task.scheduled_time }}</text>
        <text class="task-duration">{{ task.duration_minutes }}分钟</text>
      </view>
    </view>
    <view class="task-right">
      <u-tag :type="getPriorityType(task.priority)">
        {{ getPriorityText(task.priority) }}
      </u-tag>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['click', 'check']);

const checked = computed(() => props.task.status === 'completed');

const handleCheck = () => {
  emit('check', props.task.id, !checked.value);
};

const getPriorityType = (priority) => {
  const map = { 0: 'info', 1: 'warning', 2: 'error' };
  return map[priority] || 'default';
};

const getPriorityText = (priority) => {
  const map = { 0: '低', 1: '中', 2: '高' };
  return map[priority] || '-';
};
</script>
```

### 状态管理

#### 1. Pinia Store 最佳实践

```javascript
// store/goal.js
import { defineStore } from 'pinia';
import { getGoals, createGoal, updateGoal, deleteGoal } from '@/api/goal';

export const useGoalStore = defineStore('goal', {
  state: () => ({
    goals: [],
    currentGoal: null,
    loading: false,
  }),
  
  getters: {
    ongoingGoals: (state) => state.goals.filter(g => g.status === 'ongoing'),
    completedGoals: (state) => state.goals.filter(g => g.status === 'completed'),
    totalProgress: (state) => {
      if (state.goals.length === 0) return 0;
      return state.goals.reduce((sum, g) => sum + g.progress, 0) / state.goals.length;
    },
  },
  
  actions: {
    async fetchGoals() {
      this.loading = true;
      try {
        const res = await getGoals();
        this.goals = res.data.items;
      } finally {
        this.loading = false;
      }
    },
    
    async createGoal(goalData) {
      const res = await createGoal(goalData);
      this.goals.unshift(res.data);
      return res.data;
    },
    
    async updateGoal(goalId, data) {
      await updateGoal(goalId, data);
      const index = this.goals.findIndex(g => g.id === goalId);
      if (index !== -1) {
        this.goals[index] = { ...this.goals[index], ...data };
      }
    },
    
    async deleteGoal(goalId) {
      await deleteGoal(goalId);
      this.goals = this.goals.filter(g => g.id !== goalId);
    },
  },
});
```

### 路由和页面配置

**pages.json**
```json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "托管人生"
      }
    },
    {
      "path": "pages/goal/list",
      "style": {
        "navigationBarTitleText": "我的目标"
      }
    },
    {
      "path": "pages/goal/create",
      "style": {
        "navigationBarTitleText": "创建目标"
      }
    },
    {
      "path": "pages/calendar/index",
      "style": {
        "navigationBarTitleText": "日程日历"
      }
    },
    {
      "path": "pages/statistics/index",
      "style": {
        "navigationBarTitleText": "数据统计"
      }
    },
    {
      "path": "pages/profile/index",
      "style": {
        "navigationBarTitleText": "个人中心"
      }
    }
  ],
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#1989fa",
    "backgroundColor": "#ffffff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "static/icons/home.png",
        "selectedIconPath": "static/icons/home-active.png"
      },
      {
        "pagePath": "pages/calendar/index",
        "text": "日历",
        "iconPath": "static/icons/calendar.png",
        "selectedIconPath": "static/icons/calendar-active.png"
      },
      {
        "pagePath": "pages/statistics/index",
        "text": "统计",
        "iconPath": "static/icons/statistics.png",
        "selectedIconPath": "static/icons/statistics-active.png"
      },
      {
        "pagePath": "pages/profile/index",
        "text": "我的",
        "iconPath": "static/icons/profile.png",
        "selectedIconPath": "static/icons/profile-active.png"
      }
    ]
  }
}
```

---

## 后端开发

### 项目结构

```
backend/
├── app/
│   ├── api/              # 路由和API端点
│   │   ├── __init__.py
│   │   ├── deps.py      # 依赖注入
│   │   ├── auth.py      # 认证相关
│   │   ├── users.py     # 用户API
│   │   ├── goals.py     # 目标API
│   │   ├── plans.py     # 规划API
│   │   ├── tasks.py     # 任务API
│   │   ├── reminders.py # 提醒API
│   │   └── statistics.py # 统计API
│   ├── core/            # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py   # 配置文件
│   │   ├── security.py  # 安全相关
│   │   └── database.py  # 数据库配置
│   ├── models/          # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── goal.py
│   │   ├── plan.py
│   │   ├── task.py
│   │   └── reminder.py
│   ├── schemas/         # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── goal.py
│   │   ├── plan.py
│   │   ├── task.py
│   │   └── reminder.py
│   ├── services/        # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── goal_service.py
│   │   ├── plan_service.py
│   │   ├── task_service.py
│   │   ├── reminder_service.py
│   │   └── ai_service.py
│   └── utils/           # 工具函数
│       ├── __init__.py
│       ├── date.py
│       └── push.py
├── tests/               # 测试
├── alembic/             # 数据库迁移
├── main.py              # 应用入口
├── requirements.txt     # 依赖
├── Dockerfile           # Docker配置
└── .env                 # 环境变量
```

### 快速开始

#### 1. 配置环境变量

创建 `.env` 文件:

```env
# 应用配置
APP_NAME=LifeManager
APP_VERSION=1.0.0
DEBUG=True

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/lifemanager
# 或使用 SQLite
# DATABASE_URL=sqlite:///./lifemanager.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI服务配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# FCM配置
FCM_SERVER_KEY=your-fcm-server-key

# 短信服务配置
SMS_API_KEY=your-sms-api-key
```

#### 2. 数据库迁移

```bash
# 初始化迁移
alembic init alembic

# 创建迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

#### 3. 启动开发服务器

```bash
# 使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python main.py
```

### 核心功能开发

#### 1. 数据库模型

**app/models/user.py**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100))
    avatar_url = Column(String(500))
    fcm_token = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**app/models/goal.py**
```python
from sqlalchemy import Column, Integer, String, Text, Date, SmallInt, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_date = Column(Date)
    priority = Column(SmallInt, default=1)  # 0:低, 1:中, 2:高
    status = Column(String(20), default="planning")  # planning, ongoing, completed, paused
    progress = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="goals")
    plans = relationship("Plan", back_populates="goal", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="goal")
```

#### 2. Pydantic 模式

**app/schemas/goal.py**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_date: Optional[date] = None
    priority: int = Field(0, ge=0, le=2)


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    target_date: Optional[date] = None
    priority: Optional[int] = Field(None, ge=0, le=2)
    status: Optional[str] = None


class GoalResponse(GoalBase):
    id: int
    user_id: int
    status: str
    progress: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
```

#### 3. API 端点

**app/api/goals.py**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from app.services.goal_service import GoalService

router = APIRouter()


@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新目标"""
    service = GoalService(db)
    return service.create_goal(current_user.id, goal_data)


@router.get("/", response_model=List[GoalResponse])
async def get_goals(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取目标列表"""
    service = GoalService(db)
    return service.get_user_goals(current_user.id, status, skip, limit)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取目标详情"""
    service = GoalService(db)
    goal = service.get_goal(goal_id)
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限访问此目标")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新目标"""
    service = GoalService(db)
    goal = service.get_goal(goal_id)
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此目标")
    return service.update_goal(goal_id, goal_data)


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除目标"""
    service = GoalService(db)
    goal = service.get_goal(goal_id)
    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此目标")
    service.delete_goal(goal_id)
    return {"code": 200, "message": "删除成功", "data": None}
```

#### 4. 业务逻辑层

**app/services/ai_service.py**
```python
from typing import Dict, List
from openai import OpenAI
from app.core.config import settings


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_plan(self, goal: str, preference: str = "") -> Dict:
        """
        为目标生成规划
        
        Args:
            goal: 目标描述
            preference: 用户偏好
            
        Returns:
            生成的规划
        """
        prompt = f"""
        我需要完成以下目标: {goal}
        用户偏好: {preference}
        
        请帮我生成一个详细的执行计划，包括:
        1. 总体步骤分解
        2. 每个步骤的预计时间
        3. 每个步骤的具体任务
        
        请以JSON格式返回，格式如下:
        {{
            "title": "计划标题",
            "description": "计划描述",
            "estimated_hours": 总小时数,
            "stages": [
                {{
                    "stage": 阶段序号,
                    "title": "阶段标题",
                    "tasks": [
                        {{
                            "title": "任务标题",
                            "estimated_hours": 小时数,
                            "description": "任务描述"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的目标规划助手"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            import json
            content = response.choices[0].message.content
            # 提取JSON部分
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            raise Exception(f"AI规划生成失败: {str(e)}")
```

**app/services/task_service.py**
```python
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, datetime, time, timedelta
from app.models.task import Task, TaskCompletion
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.goal_service import GoalService


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.goal_service = GoalService(db)
    
    def create_task(self, user_id: int, task_data: TaskCreate) -> Task:
        """创建任务"""
        task = Task(**task_data.dict())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_today_tasks(self, user_id: int) -> Dict:
        """获取今日任务"""
        today = date.today()
        tasks = self.db.query(Task).filter(
            Task.scheduled_date == today
        ).all()
        
        completed = [t for t in tasks if t.status == 'completed']
        pending = [t for t in tasks if t.status != 'completed']
        
        return {
            'total': len(tasks),
            'completed': len(completed),
            'pending': len(pending),
            'items': tasks
        }
    
    async def complete_task(
        self,
        task_id: int,
        actual_duration: int,
        notes: Optional[str] = None
    ) -> Dict:
        """完成任务"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise Exception("任务不存在")
        
        # 更新任务状态
        task.status = 'completed'
        
        # 记录完成信息
        completion = TaskCompletion(
            task_id=task_id,
            completed_at=datetime.now(),
            actual_duration_minutes=actual_duration,
            notes=notes
        )
        self.db.add(completion)
        
        # 更新目标进度
        self.goal_service.update_progress(task.goal_id)
        
        self.db.commit()
        self.db.refresh(task)
        
        return {
            'task_id': task_id,
            'goal_progress': self.goal_service.get_progress(task.goal_id)
        }
```

#### 5. 应用入口

**main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, goals, plans, tasks, reminders, statistics

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="托管人生 - 智能目标管理应用"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/v1/users", tags=["用户"])
app.include_router(goals.router, prefix="/v1/goals", tags=["目标"])
app.include_router(plans.router, prefix="/v1/plans", tags=["规划"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["任务"])
app.include_router(reminders.router, prefix="/v1/reminders", tags=["提醒"])
app.include_router(statistics.router, prefix="/v1/statistics", tags=["统计"])

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 定时任务

使用 Celery 实现定时任务:

**app/worker.py**
```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "lifemanager",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_schedule={
        'check-reminders-every-minute': {
            'task': 'app.tasks.reminder.check_reminders',
            'schedule': 60.0,
        },
    },
)
```

**app/tasks/reminder.py**
```python
from app.worker import celery_app
from app.core.database import SessionLocal
from app.services.reminder_service import ReminderService
from app.utils.push import send_push_notification


@celery_app.task
def check_reminders():
    """检查并发送提醒"""
    db = SessionLocal()
    try:
        service = ReminderService(db)
        pending_reminders = service.get_pending_reminders()
        
        for reminder in pending_reminders:
            # 发送推送通知
            send_push_notification(
                reminder.user.fcm_token,
                title="任务提醒",
                body=reminder.message
            )
            
            # 更新提醒状态
            service.mark_as_sent(reminder.id)
            
    finally:
        db.close()
```

启动 Celery:
```bash
# 启动 worker
celery -A app.worker worker --loglevel=info

# 启动 beat (定时任务调度器)
celery -A app.worker beat --loglevel=info
```

### 测试

**tests/test_goals.py**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, Base, engine
from app.models.user import User


client = TestClient(app)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db: Session):
    user = User(
        phone="13800138000",
        password_hash="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_goal(db: Session, test_user: User):
    # 需要先获取token
    response = client.post(
        "/v1/auth/login",
        json={"phone": "13800138000", "password": "password123"}
    )
    token = response.json()["data"]["token"]
    
    # 创建目标
    response = client.post(
        "/v1/goals",
        json={
            "title": "学习Python",
            "description": "3个月内掌握Python",
            "target_date": "2026-04-23",
            "priority": 2
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "学习Python"
```

运行测试:
```bash
pytest tests/ -v
```

---

## 部署指南

### Docker 部署

**deployment/docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: lifemanager
      POSTGRES_USER: lifemanager
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://lifemanager:password@postgres:5432/lifemanager
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ../frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend

volumes:
  postgres_data:
```

启动:
```bash
cd deployment
docker-compose up -d
```

### 云服务器部署

推荐使用腾讯云或阿里云。

1. 购买服务器
2. 安装 Docker
3. 克隆代码
4. 配置环境变量
5. 启动服务

详细步骤请参考 `DEPLOYMENT.md` 文档。

---

## 常见问题

### 1. 跨域问题

在开发环境中，确保后端配置了正确的CORS设置。

### 2. 数据库连接失败

检查 `.env` 文件中的数据库URL配置是否正确。

### 3. WebSocket 连接失败

检查 WebSocket URL 是否配置正确，Token 是否有效。

### 4. 推送通知不工作

检查 FCM Token 是否有效，服务器密钥是否配置正确。

---

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

MIT License
