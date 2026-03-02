# LifeManager 项目规则

## 概述

本文档梳理 LifeManager 项目的核心规则和约定，作为开发和协作的指导原则。

**更新时间**: 2026-01-29
**版本**: 1.0.0

---

## 1. 智能体协作规则

### 核心原则
- **基于角色的智能体执行**: 所有专业操作必须通过对应角色的智能体完成
- **职责分工明确**: 每个智能体限定在专业领域内工作
- **输出切实可行**: 所有输出必须包含可执行的操作步骤或代码

### 智能体映射

| 智能体 | 关键词 | 优先级 |
|--------|--------|--------|
| Python后端工程师 | Python, FastAPI, 后端, API, 数据库 | 高 |
| Vue3前端开发工程师 | Vue3, 前端, 组件, UI, 状态管理 | 高 |
| 测试开发工程师 | 测试, 自动化测试, 质量验证, pytest | 高 |
| 产品经理 | 产品, 需求, PRD, 用户体验 | 中 |
| 项目经理 | 项目管理, 任务规划, 进度跟踪 | 中 |
| 技术架构师 | 架构, 设计, 选型, 技术栈 | 中 |
| DevOps工程师 | 部署, CI/CD, Docker, 容器 | 中 |
| Agent管理专家 | 智能体, Agent, 管理, Skill | 特殊 |

### 协作模式

| 模式 | 适用场景 | 执行方式 |
|------|----------|----------|
| 顺序 | 前后依赖 | Agent1 → Agent2 → Agent3 |
| 并行 | 独立任务 | Agent1和Agent2同时执行 → 整合 |
| 层级 | 主从关系 | 主Agent规划 → 子Agent执行 |

---

## 2. 测试规则

### 测试层级

```
tests/
├── integration/    # 集成测试（后端API测试）
│   ├── conftest.py         # pytest配置
│   ├── test_api_flow.py     # API流程测试
│   └── test_database.py     # 数据库集成测试
├── e2e/            # 端到端测试（前后端联调）
└── data/           # 测试数据
```

### 集成测试规范

**配置文件**: `tests/integration/conftest.py`
- 使用独立的测试数据库（`test_integration.db`）
- 每个测试函数创建独立的数据库会话
- 自动清理测试数据

**测试分类**:
- **TestAuthFlow**: 认证流程测试
- **TestGoalFlow**: 目标管理流程测试
- **TestPlanFlow**: 规划流程测试
- **TestDatabaseOperations**: 数据库操作测试

**运行测试**:
```bash
cd backend
python -m pytest tests/integration/ -v
```

### 测试修复流程

1. 先写测试 → 发现问题
2. 查看接口文档确认正确格式
3. 根据错误类型定位问题：
   - 405 Method Not Allowed → 检查路由定义
   - 404 Not Found → 检查路由路径和main.py注册
   - 422 Validation Error → 检查Pydantic schema
   - 500 Internal Server Error → 查看后端日志
4. 修复代码（通过对应智能体）
5. 重新测试验证

---

## 3. 代码规范

### 后端代码（FastAPI）

**目录结构**:
```
backend/
├── app/
│   ├── api/           # API路由
│   ├── core/          # 核心配置（数据库、安全、响应）
│   ├── models/        # SQLAlchemy模型
│   ├── schemas/       # Pydantic schema
│   ├── services/      # 业务逻辑
│   └── utils/         # 工具函数
└── main.py            # 应用入口
```

**API命名规范**:
- 路由前缀: `/api/{module}`
- 响应格式: `{code, message, data}`
- 认证: JWT Bearer Token

**Schema定义规则**:
- `GoalBase`: 基础字段
- `GoalCreate`: 继承GoalBase，用于创建
- `GoalUpdate`: 所有字段Optional，用于更新
- `GoalResponse`: 响应数据结构

### 前端代码（Vue3 + Uni-app）

**目录结构**:
```
frontend/
├── api/           # API接口
├── components/    # 组件
├── pages/         # 页面
├── store/         # 状态管理（Pinia）
└── utils/         # 工具函数
```

**组件规范**:
- MVP阶段使用Uni-app原生组件 + CSS样式
- 不开发自定义组件库（避免维护开销）
- 后续Phase 2可考虑引入uni-ui

---

## 4. 文档规范

### API文档

**位置**: `docs/phase1/API接口文档.md`

**内容要求**:
- Base URL: `http://localhost:8000/api`
- 通用响应格式: `{code, message, data}`
- 接口定义: 方法、路径、参数、响应示例

### 产品文档

**位置**: `docs/phase1/`
- `PRD.md` - 产品需求文档
- `UI设计文档.md` - UI设计规范
- `MVP_GUIDE.md` - MVP开发指南

---

## 5. 开发流程规则

### 需求开发流程

1. **需求分析**: 产品经理编写PRD
2. **架构设计**: 技术架构师设计技术方案
3. **开发实现**: 前后端工程师并行开发
4. **集成测试**: 测试工程师进行集成测试
5. **部署上线**: DevOps工程师部署

### 测试驱动修复流程

**重要**: 必须遵循"先写测试 → 发现问题 → 修复代码 → 验证通过"的流程

**步骤**:
1. 根据业务需求编写测试用例
2. 执行测试，收集错误信息
3. 查看API接口文档确认正确格式
4. 通过对应智能体修复代码
5. 重新运行测试验证

---

## 6. 版本管理规则

### Git分支策略

- `master`: 生产环境代码
- `develop`: 开发主分支
- `feature/*`: 功能开发分支
- `bugfix/*`: Bug修复分支

### 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 代码重构
- `chore`: 构建/工具配置

---

## 7. 环境配置规则

### 环境变量

**文件**: `backend/.env`

**必需配置**:
```
DATABASE_URL=sqlite:///./lifemanager.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI配置
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_KEY=your-api-key
AI_MODEL=gpt-3.5-turbo
```

### 测试环境

- 测试数据库: `test_integration.db`
- 环境变量: `TESTING=true`
- 自动清理: 每次测试后重置数据库

---

## 8. 质量保证规则

### 代码审查

- [ ] 命名符合规范
- [ ] 逻辑清晰简洁
- [ ] 错误处理完善
- [ ] 测试覆盖充分
- [ ] 文档更新及时

### 测试要求

- 单元测试: 核心业务逻辑
- 集成测试: API接口和数据库交互
- E2E测试: 前后端完整流程

---

## 9. 部署规则

### 部署前检查清单

- [ ] 所有测试通过
- [ ] 环境变量配置正确
- [ ] 数据库迁移脚本准备
- [ ] 回滚方案准备
- [ ] 监控告警配置

---

## 10. 附录

### 关键文件索引

| 文件 | 说明 |
|------|------|
| `.codebuddy/rules/agent_butler.mdc` | 智能体协作规则（详细） |
| `backend/app/core/response.py` | 统一响应格式 |
| `docs/phase1/API接口文档.md` | API完整文档 |
| `tests/README.md` | 测试框架说明 |

### 常见问题

**Q: 如何添加新的API接口？**
1. 在 `backend/app/api/` 创建路由文件
2. 在 `main.py` 注册路由
3. 在 `schemas/` 定义请求/响应schema
4. 编写集成测试

**Q: 测试失败如何排查？**
1. 查看错误类型（405/404/422/500）
2. 查看 `docs/phase1/API接口文档.md` 确认接口格式
3. 检查后端日志和数据库状态
4. 通过对应智能体修复

---

**待扩展项**:
- [ ] 添加前端开发规范详情
- [ ] 补充数据库迁移规范
- [ ] 添加性能优化指南
- [ ] 完善安全规范
