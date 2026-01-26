# 托管人生 (LifeManager) 应用架构设计

## 1. 项目概述

**应用名称**: 托管人生 (LifeManager)

**核心功能**: 用户告诉应用自己的目标和愿望，应用智能规划执行路径，安排日程，并在合适时间提醒用户，帮助用户达成目标。

## 2. 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **移动端框架**: Uni-app / Vant UI
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **本地存储**: LocalStorage / SQLite (Uni-app内置)

### 后端
- **语言**: Python 3.10+
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **任务队列**: Celery + Redis
- **AI集成**: OpenAI API / 本地LLM (用于智能规划)
- **推送服务**: Firebase Cloud Messaging (FCM) / 个推

### DevOps
- **容器**: Docker + Docker Compose
- **部署**: 腾讯云 / 阿里云
- **CI/CD**: GitHub Actions

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                         客户端层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   首页模块   │  │   规划模块   │  │  日历模块   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   提醒模块   │  │   统计模块   │  │   设置模块   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼─────────────────────────────────────┐
│                         API网关层                           │
│                    (FastAPI + Nginx)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                         应用层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 用户服务     │  │ 目标服务     │  │ 规划服务     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 任务服务     │  │ 提醒服务     │  │ AI规划服务   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                         数据层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL   │  │    Redis     │  │   对象存储   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                         外部服务                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   FCM推送    │  │  AI模型API   │  │  短信服务    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 4. 数据库设计

### 4.1 核心表结构

#### users (用户表)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    fcm_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### goals (目标表)
```sql
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    target_date DATE,
    priority INTEGER DEFAULT 0, -- 0:低, 1:中, 2:高
    status VARCHAR(20) DEFAULT 'planning', -- planning, ongoing, completed, paused
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### plans (规划表)
```sql
CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES goals(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    estimated_hours INTEGER,
    ai_generated BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### tasks (任务表)
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES plans(id),
    goal_id INTEGER REFERENCES goals(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME,
    duration_minutes INTEGER,
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, skipped
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### reminders (提醒表)
```sql
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    user_id INTEGER REFERENCES users(id),
    remind_time TIMESTAMP NOT NULL,
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### task_completions (任务完成记录表)
```sql
CREATE TABLE task_completions (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_duration_minutes INTEGER,
    notes TEXT
);
```

## 5. 核心功能模块

### 5.1 前端模块

#### 5.1.1 首页模块
- 今日任务列表
- 快速添加任务入口
- 目标进度概览
- 即将到来的提醒

#### 5.1.2 目标管理模块
- 创建新目标
- 查看目标详情
- 编辑目标
- 目标进度追踪
- 目标完成历史

#### 5.1.3 智能规划模块
- 输入目标/愿望
- AI生成执行规划
- 规划确认和调整
- 规划拆解为具体任务

#### 5.1.4 日历模块
- 月视图/周视图/日视图
- 任务展示
- 快速添加任务
- 任务拖拽调整

#### 5.1.5 提醒模块
- 提醒设置
- 提醒历史
- 提醒方式配置（推送、震动、铃声）

#### 5.1.6 统计分析模块
- 任务完成率统计
- 时间投入分析
- 目标达成情况
- 每日/每周/每月报表

#### 5.1.7 个人中心模块
- 用户信息管理
- 偏好设置
- 数据同步
- 反馈与帮助

### 5.2 后端服务

#### 5.2.1 用户服务
- 用户注册/登录
- 手机验证码
- 密码重置
- 用户信息管理

#### 5.2.2 目标服务
- CRUD操作
- 目标状态管理
- 目标进度计算

#### 5.2.3 规划服务
- 调用AI生成规划
- 规划版本管理
- 规划调整

#### 5.2.4 任务服务
- 任务CRUD
- 任务状态流转
- 任务调度

#### 5.2.5 提醒服务
- 定时任务扫描
- 推送通知
- 提醒记录

#### 5.2.6 统计服务
- 数据聚合
- 报表生成
- 可视化数据

#### 5.2.7 AI规划服务
- 自然语言理解
- 目标拆解算法
- 时间估算
- 任务优先级排序

## 6. 关键流程

### 6.1 用户创建目标并生成规划流程
```
1. 用户在前端输入目标描述
2. 前端调用 POST /api/goals 创建目标
3. 后端调用AI服务分析目标，生成规划
4. 返回规划给用户确认
5. 用户确认后，规划拆解为任务
6. 根据用户日程安排任务时间
7. 创建对应的提醒记录
```

### 6.2 提醒触发流程
```
1. 定时任务每分钟扫描即将到期的提醒
2. 对于到期的提醒，通过FCM发送推送
3. 记录推送状态
4. 更新任务状态
```

### 6.3 任务完成流程
```
1. 用户标记任务完成
2. 记录完成时间和实际耗时
3. 更新目标进度
4. 触发统计更新
5. 生成下一个阶段的任务（如需要）
```

## 7. 技术难点和解决方案

### 7.1 AI智能规划
**难点**: 如何将模糊的目标转化为可执行的具体任务
**方案**: 
- 使用大语言模型（GPT-4/本地LLM）进行目标理解和拆解
- 建立任务模板库
- 人工审核和调整机制

### 7.2 时间安排优化
**难点**: 如何在有限时间内合理安排任务
**方案**:
- 收集用户的时间偏好和历史数据
- 使用启发式算法进行任务排期
- 允许用户手动调整

### 7.3 提醒准确性
**难点**: 确保提醒及时送达且不被用户忽略
**方案**:
- 多重提醒机制（推送、震动、铃声）
- 智能提醒时机选择（基于用户习惯）
- 提醒效果反馈和优化

### 7.4 跨平台推送
**难点**: Android/iOS推送差异
**方案**:
- 使用Firebase Cloud Messaging
- 备用个推服务（国内环境）

## 8. 安全性设计

### 8.1 认证授权
- JWT Token认证
- Token刷新机制
- 设备绑定管理

### 8.2 数据安全
- 密码加密存储
- HTTPS传输
- 敏感数据脱敏

### 8.3 接口安全
- 请求签名
- 频率限制
- SQL注入防护

## 9. 性能优化

### 9.1 前端优化
- 虚拟滚动
- 图片懒加载
- 代码分割
- 离线缓存

### 9.2 后端优化
- 数据库索引
- Redis缓存
- 异步任务队列
- 数据库连接池

## 10. 部署方案

### 10.1 开发环境
- Docker Compose一键启动
- 本地PostgreSQL + Redis

### 10.2 生产环境
- 腾讯云CVM
- PostgreSQL RDS
- Redis集群
- Nginx反向代理
- SSL证书

## 11. 项目目录结构

```
LifeManager/
├── frontend/                 # 前端项目（Uni-app + Vue3）
│   ├── pages/               # 页面
│   ├── components/          # 组件
│   ├── store/               # Pinia状态管理
│   ├── utils/               # 工具函数
│   ├── api/                 # API封装
│   ├── static/              # 静态资源
│   └── manifest.json        # Uni-app配置
├── backend/                 # 后端项目
│   ├── app/                 # 应用主目录
│   │   ├── api/             # 路由和API
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic模式
│   │   ├── services/        # 业务逻辑层
│   │   ├── core/            # 核心配置
│   │   └── utils/           # 工具函数
│   ├── tests/               # 测试
│   ├── requirements.txt     # 依赖
│   └── Dockerfile           # Docker配置
├── deployment/              # 部署配置
│   ├── docker-compose.yml
│   └── nginx.conf
└── docs/                    # 文档
    ├── API.md              # API文档
    ├── DATABASE.md         # 数据库文档
    └── DEVELOPMENT.md      # 开发指南
```

## 12. 开发阶段规划

### Phase 1: 基础框架搭建 (2周)
- 前端Uni-app项目初始化
- 后端FastAPI项目初始化
- 数据库设计和迁移
- 基础UI组件库搭建

### Phase 2: 核心功能开发 (3周)
- 用户注册登录
- 目标CRUD
- 基础任务管理
- 日历视图

### Phase 3: 智能规划功能 (2周)
- AI服务集成
- 规划生成逻辑
- 规划确认流程

### Phase 4: 提醒系统 (1周)
- 定时任务调度
- 推送通知集成
- 提醒管理

### Phase 5: 统计分析 (1周)
- 数据统计
- 可视化图表
- 报表导出

### Phase 6: 测试和优化 (1周)
- 单元测试
- 集成测试
- 性能优化
- Bug修复

### Phase 7: 上线准备 (1周)
- 打包上架
- 服务器部署
- 监控配置
