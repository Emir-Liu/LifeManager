# 托管人生 (LifeManager)

> AI 智能人生管理助手 - 让 AI 帮你规划人生

## 📖 文档导航

本项目采用 **MVP 优先** 的开发策略，详细文档请查看 [docs/README.md](docs/README.md)

- [📚 完整文档目录](docs/README.md)
- [🎯 MVP 文档导航](docs/phase1/MVP_README.md)
- [🚀 快速开始](docs/phase1/MVP_GUIDE.md#快速开始)

## 🎯 项目简介

托管人生是一款基于 AI 的人生管理应用，通过智能算法帮助用户：
- 设定人生目标
- 自动生成可执行的规划
- 跟踪任务完成情况
- 实现人生目标

## 🏗️ 技术栈

- **前端**: Vue 3 + Uni-app + HBuilderX
- **后端**: FastAPI + SQLite
- **AI**: OpenAI/DeepSeek API
- **部署**: Docker

## 📅 开发阶段

### 第一阶段：MVP 核心功能（当前进行中）

**目标**: 实现 AI 智能规划的核心价值

**时间**: 2-3 周

**功能**:
- ✅ 用户注册登录
- ✅ 目标创建和管理
- ⭐ **AI 规划生成**（核心）
- ✅ 规划查看和确认
- ✅ 任务自动创建
- ✅ 任务列表和完成

**交付物**: 可在安卓手机上运行的 APP

### 第二阶段：增强功能

- 提醒通知系统
- 数据统计和可视化
- 日历视图
- 任务编辑和管理

### 第三阶段：多平台支持

- 微信小程序版本
- iOS APP 版本
- Web H5 版本

## 🚀 快速开始

```bash
# 前端开发（使用 HBuilderX）
打开 e:/project/LifeManager/frontend
运行 → 运行到浏览器/手机

# 后端开发
cd e:/project/LifeManager/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py

# 访问 API 文档
# http://localhost:8000/docs
```

## 📊 当前进度

| 模块 | 进度 | 说明 |
|------|------|------|
| 前端框架 | ✅ 100% | Vue 3 + Uni-app 项目已创建 |
| 后端框架 | ✅ 100% | FastAPI 项目已创建 |
| 用户系统 | ✅ 100% | 登录注册页面和接口 |
| 目标管理 | ✅ 100% | 目标 CRUD 功能 |
| AI 规划生成 | ⏳ 0% | **核心功能，待开发** |
| 规划确认 | ⏳ 0% | 待开发 |
| 任务管理 | ⏳ 0% | 待开发 |

**总体进度**: 约 40%

## 📂 项目结构

```
LifeManager/
├── docs/              # 项目文档
│   ├── README.md      # 文档导航
│   ├── phase1/        # MVP 核心功能
│   ├── phase2/        # 增强功能
│   └── phase3/        # 多平台和优化
├── backend/           # 后端代码
│   ├── app/           # 应用主目录
│   ├── main.py        # 应用入口
│   └── requirements.txt
├── frontend/          # 前端代码
│   ├── api/           # API 接口
│   ├── components/    # 组件
│   ├── pages/         # 页面
│   ├── store/         # 状态管理
│   └── utils/         # 工具函数
└── deployment/        # 部署配置
    └── docker-compose.yml
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
