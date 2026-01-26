# 托管人生 (LifeManager)

> 智能目标管理应用，让你的生活更有规划

## 项目简介

托管人生是一款基于人工智能的个人目标管理应用。用户只需告诉应用自己的目标和愿望，应用就会智能生成执行规划，安排具体任务，并在合适的时间提醒用户，帮助用户达成目标。

### 核心功能

- 🎯 **智能目标管理**: 设定目标，AI自动生成执行规划
- 📅 **智能日程安排**: 根据用户偏好自动安排任务时间
- ⏰ **智能提醒**: 任务时间到，自动推送提醒
- 📊 **数据统计分析**: 可视化展示完成情况，帮助改进
- 📱 **多端同步**: 支持 Android/iOS 多平台

### 技术栈

**前端**:
- Vue 3 (Composition API)
- Uni-app (跨平台)
- Pinia (状态管理)
- Vant UI (组件库)

**后端**:
- Python 3.10+
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- PostgreSQL (数据库)
- Redis (缓存)
- Celery (异步任务)
- OpenAI GPT (AI规划)

**部署**:
- Docker + Docker Compose
- Nginx (反向代理)

## 项目结构

```
LifeManager/
├── docs/                 # 📚 项目文档
│   ├── README.md        # 文档导航
│   ├── ARCHITECTURE.md  # 架构设计文档
│   ├── API.md          # API接口文档
│   ├── DATABASE.md     # 数据库设计文档
│   ├── DEVELOPMENT.md  # 开发指南
│   ├── PROJECT_STRUCTURE.md # 项目结构说明
│   └── DEPLOYMENT.md   # 部署指南
├── frontend/            # 前端项目 (Uni-app + Vue3)
├── backend/             # 后端项目 (FastAPI + Python)
├── deployment/          # 部署配置
├── README.md            # 本文件
└── .gitignore          # Git忽略文件配置
```

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker (可选)

### 文档阅读顺序

1. **[架构设计文档](docs/ARCHITECTURE.md)** - 了解系统整体架构和技术方案
2. **[开发指南](docs/DEVELOPMENT.md)** - 搭建开发环境
3. **[API接口文档](docs/API.md)** - 了解API接口规范
4. **[数据库设计文档](docs/DATABASE.md)** - 了解数据库设计
5. **[部署指南](docs/DEPLOYMENT.md)** - 了解部署方案

详细文档请查看 [docs/](docs/) 目录。

### 使用 Docker 启动 (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 访问应用

- 前端页面: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 数据库: localhost:5432

## 功能演示

### 1. 创建目标
用户输入想要达成的目标，例如"在3个月内学会Python"。

### 2. AI 生成规划
应用调用 AI 服务，分析目标并生成详细的执行规划。

### 3. 确认规划
用户可以查看、修改并确认规划。

### 4. 自动安排任务
系统根据用户的时间偏好，自动将规划拆解为具体任务并安排到日历中。

### 5. 任务提醒
在任务开始前，应用会发送推送提醒用户。

### 6. 完成任务
用户完成任务后，系统记录完成情况并更新目标进度。

### 7. 数据统计
用户可以查看各种统计数据，了解自己的执行情况。

## 开发计划

### Phase 1: 基础框架 (2周)
- [x] 项目结构设计
- [ ] 前后端框架搭建
- [ ] 数据库设计
- [ ] 基础UI组件

### Phase 2: 核心功能 (3周)
- [ ] 用户系统
- [ ] 目标管理
- [ ] 任务管理
- [ ] 日历视图

### Phase 3: 智能规划 (2周)
- [ ] AI 服务集成
- [ ] 规划生成逻辑
- [ ] 规划确认流程

### Phase 4: 提醒系统 (1周)
- [ ] 定时任务
- [ ] 推送通知
- [ ] 提醒管理

### Phase 5: 统计分析 (1周)
- [ ] 数据统计
- [ ] 可视化图表
- [ ] 报表导出

### Phase 6: 测试优化 (1周)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化

### Phase 7: 上线发布 (1周)
- [ ] 打包上架
- [ ] 服务器部署
- [ ] 监控配置

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 开发规范

### 代码规范

- 前端遵循 [Vue 风格指南](https://cn.vuejs.org/v2/style-guide/)
- 后端遵循 [PEP 8](https://peps.python.org/pep-0008/)
- 使用 ESLint 和 Prettier 格式化前端代码
- 使用 Black 和 Flake8 格式化后端代码

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范:

```
feat: 添加新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

## 常见问题

### Q1: 数据库连接失败

检查 `.env` 文件中的数据库配置是否正确，确保 PostgreSQL 服务已启动。

### Q2: 推送通知不工作

检查 FCM Token 是否有效，服务器密钥是否配置正确。

### Q3: AI 规划生成失败

检查 OpenAI API Key 是否有效，确保账户有足够的配额。

## 文档索引

| 文档 | 说明 |
|------|------|
| [架构设计](docs/ARCHITECTURE.md) | 系统架构、技术栈、核心模块 |
| [API接口](docs/API.md) | 完整的API接口文档 |
| [数据库设计](docs/DATABASE.md) | 数据库表结构和关系 |
| [开发指南](docs/DEVELOPMENT.md) | 开发环境和最佳实践 |
| [项目结构](docs/PROJECT_STRUCTURE.md) | 目录结构说明 |
| [部署指南](docs/DEPLOYMENT.md) | Docker和传统部署方案 |

## 联系方式

- 项目主页: https://github.com/yourusername/LifeManager
- 问题反馈: https://github.com/yourusername/LifeManager/issues
- 邮箱: your.email@example.com

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

感谢所有为本项目贡献代码、提供建议和帮助测试的朋友们！

---

**托管人生 - 让你的生活更有规划** 🚀
