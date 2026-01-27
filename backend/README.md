# LifeManager Backend

基于 FastAPI 的后端服务，提供目标管理、AI 智能规划等功能。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发环境
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的参数
```

### 数据库配置说明

本项目支持多种数据库: SQLite、MySQL、PostgreSQL。

#### 使用 SQLite(开发环境)
```bash
# .env 文件中配置
DATABASE_URL=sqlite:///./lifemanager.db
```
无需额外配置,开箱即用。

#### 使用 MySQL(生产环境推荐)
数据库创建脚本
```bash
docker run -d \
  --name lifemanager-mysql \
  --restart unless-stopped \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=lifemanager \
  -e MYSQL_USER=lifemanager \
  -e MYSQL_PASSWORD=lifemanager_password \
  -p 3306:3306 \
  -v mysql_data:/var/lib/mysql \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

1. 安装 MySQL 服务:
```bash
# Windows: 下载并安装 MySQL Installer
# macOS: brew install mysql
# Linux: sudo apt-get install mysql-server
```

2. 创建数据库:
```sql
CREATE DATABASE lifemanager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 配置 .env 文件:
```bash
DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/lifemanager?charset=utf8mb4
```

4. 首次启动时,应用会自动创建表结构。

#### 使用 PostgreSQL

1. 创建数据库:
```sql
CREATE DATABASE lifemanager;
```

2. 配置 .env 文件:
```bash
DATABASE_URL=postgresql://用户名:密码@localhost:5432/lifemanager
```

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

访问 API 文档: http://localhost:8000/docs

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_auth.py
pytest tests/test_goals.py
pytest tests/test_plans.py
pytest tests/test_tasks.py
```

### 运行特定测试用例

```bash
pytest tests/test_auth.py::TestAuth::test_register_success
```

### 生成测试覆盖率报告

```bash
pytest --cov=app --cov-report=html
```

报告将生成在 `htmlcov/index.html`。

### 测试选项

- `-v`: 显示详细输出
- `-s`: 显示 print 输出
- `--pdb`: 测试失败时进入调试器

示例:
```bash
pytest -v -s
```

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 层 - 接口定义
│   ├── services/         # Service 层 - 业务逻辑
│   ├── models/           # 模型层 - ORM 模型
│   ├── schemas/          # Schema 层 - Pydantic 模型
│   └── core/             # 核心层 - 配置、安全等
├── tests/                # 测试目录
│   ├── conftest.py       # pytest 配置
│   ├── test_auth.py      # 认证测试
│   ├── test_goals.py     # 目标测试
│   ├── test_plans.py     # 规划测试
│   └── test_tasks.py     # 任务测试
├── main.py               # 应用入口
├── requirements.txt      # 生产依赖
└── requirements-dev.txt  # 开发依赖
```

## API 接口

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出

### 目标接口

- `GET /api/goals` - 获取目标列表
- `POST /api/goals` - 创建目标
- `GET /api/goals/{id}` - 获取目标详情
- `DELETE /api/goals/{id}` - 删除目标

### 规划接口

- `POST /api/plans/generate` - 生成规划（AI）
- `GET /api/plans/{id}` - 获取规划详情
- `POST /api/plans/{id}/confirm` - 确认规划
- `PUT /api/plans/{id}` - 修改规划

### 任务接口

- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/today` - 获取今日任务
- `POST /api/tasks` - 创建任务
- `PUT /api/tasks/{id}/complete` - 完成任务
- `PUT /api/tasks/{id}/uncomplete` - 取消完成
- `DELETE /api/tasks/{id}` - 删除任务

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEBUG` | 调试模式 | `True` |
| `DATABASE_URL` | 数据库连接 (支持 MySQL/PostgreSQL/SQLite) | `sqlite:///./lifemanager.db` |
| `JWT_SECRET_KEY` | JWT 密钥 | `your-secret-key-here` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | `10080` |
| `OPENAI_API_BASE` | OpenAI API 地址 (通用接口) | `https://api.openai.com/v1` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `AI_MODEL` | AI 模型 | `gpt-3.5-turbo` |

### 数据库 URL 格式说明

- **MySQL**: `mysql+pymysql://用户名:密码@主机:端口/数据库?charset=utf8mb4`
- **PostgreSQL**: `postgresql://用户名:密码@主机:端口/数据库`
- **SQLite**: `sqlite:///./数据库文件路径.db`

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLAlchemy ORM + MySQL / PostgreSQL / SQLite
- **MySQL 驱动**: PyMySQL
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt
- **测试**: pytest
- **日志**: loguru

## 开发指南

### 添加新的 API 接口

1. 在 `app/api/` 创建或修改路由文件
2. 在 `app/services/` 创建或修改服务层逻辑
3. 在 `app/schemas/` 创建 Pydantic 模型
4. 在 `tests/` 添加测试用例

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 许可证

MIT
