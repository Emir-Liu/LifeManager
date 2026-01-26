# LifeManager 项目结构说明

## 根目录结构

```
LifeManager/
├── frontend/                 # 前端项目 (Uni-app + Vue3)
├── backend/                  # 后端项目 (FastAPI + Python)
├── deployment/               # 部署配置
├── docs/                     # 项目文档
├── README.md                 # 项目说明
├── ARCHITECTURE.md          # 架构设计文档
├── API.md                   # API接口文档
├── DATABASE.md              # 数据库设计文档
├── DEVELOPMENT.md           # 开发指南
├── .gitignore               # Git忽略文件配置
└── docker-compose.yml       # Docker编排配置
```

---

## Frontend 目录结构详解

```
frontend/
├── pages/                   # 页面目录
│   ├── index/              # 首页
│   │   └── index.vue       # 首页组件
│   ├── auth/               # 认证相关页面
│   │   ├── login.vue       # 登录页
│   │   └── register.vue    # 注册页
│   ├── goal/               # 目标相关页面
│   │   ├── list.vue        # 目标列表
│   │   ├── create.vue      # 创建目标
│   │   ├── detail.vue      # 目标详情
│   │   └── edit.vue        # 编辑目标
│   ├── plan/               # 规划相关页面
│   │   ├── generate.vue    # 生成规划
│   │   ├── confirm.vue     # 确认规划
│   │   └── detail.vue      # 规划详情
│   ├── task/               # 任务相关页面
│   │   ├── create.vue      # 创建任务
│   │   ├── detail.vue      # 任务详情
│   │   └── edit.vue        # 编辑任务
│   ├── calendar/           # 日历页面
│   │   └── index.vue       # 日历主页面
│   ├── statistics/         # 统计页面
│   │   ├── overview.vue    # 统计概览
│   │   └── report.vue      # 详细报表
│   └── profile/            # 个人中心页面
│       ├── index.vue       # 个人中心首页
│       ├── settings.vue    # 设置页
│       └── feedback.vue     # 反馈页
│
├── components/             # 组件目录
│   ├── common/            # 通用组件
│   │   ├── Navbar.vue     # 导航栏
│   │   ├── TabBar.vue     # 底部标签栏
│   │   └── EmptyState.vue # 空状态组件
│   ├── goal/              # 目标相关组件
│   │   ├── GoalCard.vue   # 目标卡片
│   │   ├── GoalProgress.vue # 目标进度条
│   │   └── GoalFilter.vue # 目标筛选器
│   ├── task/              # 任务相关组件
│   │   ├── TaskCard.vue   # 任务卡片
│   │   ├── TaskList.vue   # 任务列表
│   │   └── TaskTimer.vue  # 任务计时器
│   ├── calendar/          # 日历组件
│   │   ├── CalendarGrid.vue # 日历网格
│   │   ├── DayView.vue    # 日视图
│   │   ├── WeekView.vue   # 周视图
│   │   └── MonthView.vue  # 月视图
│   └── reminder/          # 提醒组件
│       ├── ReminderList.vue # 提醒列表
│       └── ReminderSettings.vue # 提醒设置
│
├── store/                 # Pinia 状态管理
│   ├── index.js          # Store 入口
│   ├── user.js           # 用户状态
│   ├── goal.js           # 目标状态
│   ├── task.js           # 任务状态
│   ├── reminder.js       # 提醒状态
│   └── settings.js       # 设置状态
│
├── api/                  # API 封装
│   ├── request.js        # Axios 封装和拦截器
│   ├── auth.js          # 认证API
│   ├── user.js          # 用户API
│   ├── goal.js          # 目标API
│   ├── plan.js          # 规划API
│   ├── task.js          # 任务API
│   ├── reminder.js      # 提醒API
│   ├── statistics.js    # 统计API
│   └── settings.js      # 设置API
│
├── utils/               # 工具函数
│   ├── date.js          # 日期处理函数
│   ├── format.js        # 格式化函数
│   ├── storage.js       # 本地存储封装
│   ├── validate.js      # 表单验证
│   ├── constants.js     # 常量定义
│   └── websocket.js     # WebSocket 封装
│
├── static/              # 静态资源
│   ├── images/          # 图片资源
│   │   ├── logo.png     # Logo
│   │   └── default-avatar.png # 默认头像
│   ├── icons/           # 图标资源
│   │   ├── home.png     # 首页图标
│   │   ├── calendar.png # 日历图标
│   │   ├── statistics.png # 统计图标
│   │   └── profile.png  # 个人中心图标
│   └── fonts/           # 字体文件
│
├── styles/              # 样式文件
│   ├── variables.scss   # SCSS变量
│   ├── mixins.scss      # SCSS混入
│   └── common.scss      # 通用样式
│
├── App.vue              # 根组件
├── main.js              # 应用入口
├── manifest.json        # Uni-app 应用配置
├── pages.json           # 页面路由配置
├── uni.scss             # Uni-app 全局样式
├── package.json         # npm 依赖配置
└── vite.config.js       # Vite 构建配置
```

---

## Backend 目录结构详解

```
backend/
├── app/                  # 应用主目录
│   ├── __init__.py     # 应用初始化
│   ├── main.py         # FastAPI 应用入口
│   │
│   ├── api/            # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py     # 依赖注入
│   │   │
│   │   ├── auth.py     # 认证相关API
│   │   │   ├── router.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── users.py    # 用户API
│   │   ├── goals.py    # 目标API
│   │   ├── plans.py    # 规划API
│   │   ├── tasks.py    # 任务API
│   │   ├── reminders.py # 提醒API
│   │   ├── statistics.py # 统计API
│   │   └── settings.py # 设置API
│   │
│   ├── core/           # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py   # 配置文件
│   │   ├── security.py # 安全相关
│   │   ├── database.py # 数据库配置
│   │   └── redis.py    # Redis配置
│   │
│   ├── models/         # SQLAlchemy 数据模型
│   │   ├── __init__.py
│   │   ├── user.py     # 用户模型
│   │   ├── goal.py     # 目标模型
│   │   ├── plan.py     # 规划模型
│   │   ├── plan_stage.py # 规划阶段模型
│   │   ├── task.py     # 任务模型
│   │   ├── reminder.py # 提醒模型
│   │   ├── task_completion.py # 任务完成记录
│   │   ├── user_setting.py # 用户设置
│   │   ├── feedback.py # 反馈模型
│   │   └── statistics_cache.py # 统计缓存
│   │
│   ├── schemas/        # Pydantic 数据验证模式
│   │   ├── __init__.py
│   │   ├── auth.py     # 认证相关Schema
│   │   ├── user.py     # 用户Schema
│   │   ├── goal.py     # 目标Schema
│   │   ├── plan.py     # 规划Schema
│   │   ├── task.py     # 任务Schema
│   │   ├── reminder.py # 提醒Schema
│   │   ├── statistics.py # 统计Schema
│   │   └── common.py   # 通用Schema
│   │
│   ├── services/       # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py     # 认证服务
│   │   ├── user_service.py     # 用户服务
│   │   ├── goal_service.py     # 目标服务
│   │   ├── plan_service.py     # 规划服务
│   │   ├── task_service.py     # 任务服务
│   │   ├── reminder_service.py # 提醒服务
│   │   ├── statistics_service.py # 统计服务
│   │   ├── ai_service.py       # AI服务
│   │   └── push_service.py     # 推送服务
│   │
│   ├── utils/          # 工具函数
│   │   ├── __init__.py
│   │   ├── date.py     # 日期工具
│   │   ├── hash.py     # 哈希工具
│   │   ├── push.py     # 推送工具
│   │   ├── sms.py      # 短信工具
│   │   └── validators.py # 验证器
│   │
│   └── tasks/          # Celery 异步任务
│       ├── __init__.py
│       ├── reminder.py # 提醒任务
│       ├── statistics.py # 统计任务
│       └── cleanup.py  # 清理任务
│
├── tests/              # 测试目录
│   ├── __init__.py
│   ├── conftest.py     # pytest 配置
│   ├── test_auth.py    # 认证测试
│   ├── test_goals.py   # 目标测试
│   ├── test_tasks.py   # 任务测试
│   ├── test_api.py     # API测试
│   └── test_services.py # 服务层测试
│
├── alembic/            # 数据库迁移
│   ├── versions/       # 迁移版本文件
│   │   └── 001_initial.py
│   ├── env.py          # Alembic 环境配置
│   ├── script.py.mako  # 迁移脚本模板
│   └── README.md
│
├── scripts/            # 脚本目录
│   ├── init_db.py      # 初始化数据库
│   ├── seed_data.py    # 种子数据
│   └── test_ai.py      # AI服务测试
│
├── main.py             # 应用入口
├── worker.py           # Celery worker 配置
├── requirements.txt    # Python 依赖
├── requirements-dev.txt # 开发依赖
├── .env.example        # 环境变量示例
├── .env                # 环境变量 (不提交)
├── pytest.ini          # pytest 配置
├── .flake8             # flake8 配置
├── Dockerfile          # Docker 配置
└── README.md           # 后端说明文档
```

---

## Deployment 目录结构详解

```
deployment/
├── docker-compose.yml    # Docker 编排配置
├── docker-compose.prod.yml # 生产环境配置
├── nginx/
│   ├── nginx.conf       # Nginx 主配置
│   └── conf.d/
│       └── app.conf     # 应用配置
├── kubernetes/          # Kubernetes 配置
│   ├── deployment.yaml  # 部署配置
│   ├── service.yaml     # 服务配置
│   ├── ingress.yaml     # 入口配置
│   └── configmap.yaml   # 配置文件
├── scripts/             # 部署脚本
│   ├── deploy.sh        # 部署脚本
│   ├── backup.sh        # 备份脚本
│   └── restore.sh       # 恢复脚本
└── README.md            # 部署说明文档
```

---

## 文件说明

### 核心配置文件

#### frontend/manifest.json
Uni-app 应用配置文件，定义应用的基本信息、图标、启动页等。

```json
{
  "name": "托管人生",
  "appid": "__UNI__XXXXXX",
  "description": "智能目标管理应用",
  "versionName": "1.0.0",
  "versionCode": "100",
  "transformPx": false,
  "app-plus": {
    "usingComponents": true,
    "nvueStyleCompiler": "uni-app",
    "compilerVersion": 3,
    "splashscreen": {
      "alwaysShowBeforeRender": true,
      "waiting": true,
      "autoclose": true,
      "delay": 0
    }
  },
  "quickapp": {},
  "mp-weixin": {
    "appid": "",
    "setting": {
      "urlCheck": false
    },
    "usingComponents": true
  }
}
```

#### frontend/pages.json
页面路由配置，定义页面路径、样式、导航栏等。

```json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "托管人生",
        "enablePullDownRefresh": false
      }
    }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarTitleText": "托管人生",
    "navigationBarBackgroundColor": "#F8F8F8",
    "backgroundColor": "#F8F8F8"
  },
  "tabBar": {
    "color": "#7A7E83",
    "selectedColor": "#1989fa",
    "borderStyle": "black",
    "backgroundColor": "#ffffff",
    "list": [...]
  }
}
```

#### backend/.env
后端环境变量配置文件。

```env
# 应用配置
APP_NAME=LifeManager
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/lifemanager

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI配置
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# FCM配置
FCM_SERVER_KEY=AAA...

# 短信配置
SMS_API_KEY=...
```

#### deployment/docker-compose.yml
Docker 编排配置，定义服务依赖关系。

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
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://lifemanager:password@postgres:5432/lifemanager
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

---

## 开发工作流

### 前端开发流程

1. **初始化项目**
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**
   ```bash
   # H5
   npm run dev:h5
   
   # 微信小程序
   npm run dev:mp-weixin
   
   # APP
   npm run dev:app
   ```

3. **代码规范**
   - 使用 ESLint 检查代码
   - 使用 Prettier 格式化代码

4. **构建打包**
   ```bash
   # H5
   npm run build:h5
   
   # 微信小程序
   npm run build:mp-weixin
   
   # APP
   npm run build:app
   ```

### 后端开发流程

1. **初始化项目**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件
   ```

3. **数据库迁移**
   ```bash
   alembic upgrade head
   ```

4. **启动开发服务器**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **启动 Celery Worker** (另一个终端)
   ```bash
   celery -A app.worker worker --loglevel=info
   ```

6. **运行测试**
   ```bash
   pytest tests/
   ```

---

## Git 分支策略

```
main          # 主分支，生产环境
  │
develop       # 开发分支
  │
feature/*     # 功能分支
  │
bugfix/*      # 修复分支
  │
hotfix/*      # 热修复分支
```

### 分支命名规范

- `feature/功能名`: 开发新功能
- `bugfix/问题描述`: 修复bug
- `hotfix/问题描述`: 紧急修复
- `refactor/描述`: 代码重构
- `docs/描述`: 文档更新

---

## 代码提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(goal): 添加目标进度计算功能

- 实现目标进度自动计算
- 添加进度更新触发器
- 更新API接口

Closes #123
```

---

## 开发工具推荐

### 前端
- **IDE**: VS Code / HBuilderX
- **调试**: Chrome DevTools / 微信开发者工具
- **Git**: SourceTree / GitKraken

### 后端
- **IDE**: PyCharm / VS Code
- **API测试**: Postman / Apifox
- **数据库管理**: DBeaver / pgAdmin
- **Redis管理**: RedisInsight

### 通用
- **API文档**: Swagger UI
- **协作**: 飞书 / 钉钉
- **项目管理**: Jira / Trello

---

## 常用命令速查

### 前端
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev:h5

# 构建
npm run build:h5

# 代码检查
npm run lint

# 代码修复
npm run lint:fix
```

### 后端
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest tests/ -v

# 数据库迁移
alembic upgrade head

# 创建迁移
alembic revision --autogenerate -m "描述"
```

### Docker
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

---

## 项目扩展建议

### 短期扩展
1. 添加任务标签功能
2. 支持任务模板
3. 添加番茄钟计时器
4. 实现任务拖拽排序

### 中期扩展
1. 支持团队协作
2. 添加社交分享功能
3. 集成日历应用
4. 支持语音输入

### 长期扩展
1. AI助手对话
2. 个性化推荐
3. 游戏化元素
4. 数据导出功能
