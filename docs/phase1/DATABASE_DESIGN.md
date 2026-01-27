# LifeManager MVP 数据库设计文档

## 文档信息

- **版本**: v1.0
- **创建日期**: 2026-01-27
- **作者**: 产品经理
- **状态**: 已发布
- **适用阶段**: Phase 1 - MVP

---

## 1. 数据库概述

### 1.1 数据库选型

**数据库**: SQLite

**选型理由**:
- ✅ 快速开发，无需额外安装和配置
- ✅ 适合 MVP 阶段的轻量级应用
- ✅ 单文件存储，便于迁移和备份
- ✅ 支持 SQLAlchemy ORM

**未来规划**: 生产环境可迁移到 PostgreSQL

### 1.2 数据库连接

```python
# backend/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库 URL（从环境变量读取）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lifemanager.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 多线程支持
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 2. 数据表设计

### 2.1 用户表 (users)

**用途**: 存储用户账号信息

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 用户 ID | 1 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 | "testuser" |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 | "$2b$12$..." |
| email | VARCHAR(100) | UNIQUE | 邮箱（可选） | "test@example.com" |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | "2026-01-27 10:00:00" |

**索引**:
```sql
CREATE INDEX idx_users_username ON users(username);
```

**SQLAlchemy 模型**:
```python
# backend/app/models/user.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
```

---

### 2.2 目标表 (goals)

**用途**: 存储用户的目标信息

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 目标 ID | 1 |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | 用户 ID | 1 |
| title | VARCHAR(200) | NOT NULL | 目标标题 | "学习 Python 编程" |
| description | TEXT | NULLABLE | 目标描述 | "在3个月内掌握..." |
| deadline | DATE | NULLABLE | 截止日期 | "2025-04-26" |
| status | VARCHAR(20) | DEFAULT 'planning' | 状态 | "planning" |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | "2026-01-27 10:00:00" |
| updated_at | DATETIME | NULLABLE | 更新时间 | "2026-01-28 10:00:00" |

**状态枚举**:
- `planning` - 规划中（未生成规划）
- `confirmed` - 已确认（规划已确认）
- `completed` - 已完成

**索引**:
```sql
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_status ON goals(status);
CREATE INDEX idx_goals_deadline ON goals(deadline);
```

**外键关系**:
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

**SQLAlchemy 模型**:
```python
# backend/app/models/goal.py

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True, index=True)
    status = Column(String(20), default="planning", index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="goals")
    plans = relationship("Plan", back_populates="goal", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Goal(id={self.id}, title={self.title}, status={self.status})>"
```

---

### 2.3 规划表 (plans)

**用途**: 存储 AI 生成的规划

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 规划 ID | 1 |
| goal_id | INTEGER | FOREIGN KEY, NOT NULL | 目标 ID | 1 |
| content | TEXT | NOT NULL | 规划内容（JSON） | '{"stages": [...]}'
| status | VARCHAR(20) | DEFAULT 'draft' | 状态 | "draft" |
| total_stages | INTEGER | DEFAULT 0 | 阶段数量 | 3 |
| total_tasks | INTEGER | DEFAULT 0 | 任务数量 | 15 |
| estimated_total_hours | FLOAT | DEFAULT 0 | 预估总工时 | 30.0 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | "2026-01-27 10:00:00" |
| updated_at | DATETIME | NULLABLE | 更新时间 | "2026-01-28 10:00:00" |

**状态枚举**:
- `draft` - 草稿（AI 生成后，用户未确认）
- `confirmed` - 已确认（用户确认后）

**content 字段 JSON 结构**:
```json
{
  "stages": [
    {
      "name": "基础语法学习",
      "order": 1,
      "tasks": [
        {
          "title": "安装 Python 环境",
          "description": "下载并安装 Python 3.10+",
          "estimated_hours": 0.5,
          "order": 1
        },
        {
          "title": "学习变量和数据类型",
          "description": "理解整数、浮点数、字符串等",
          "estimated_hours": 2,
          "order": 2
        }
      ]
    }
  ]
}
```

**索引**:
```sql
CREATE INDEX idx_plans_goal_id ON plans(goal_id);
CREATE INDEX idx_plans_status ON plans(status);
```

**外键关系**:
```sql
FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
```

**SQLAlchemy 模型**:
```python
# backend/app/models/plan.py

from sqlalchemy import Column, Integer, Text, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)  # JSON 字符串
    status = Column(String(20), default="draft", index=True)
    total_stages = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    estimated_total_hours = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # 关系
    goal = relationship("Goal", back_populates="plans")
    tasks = relationship("Task", back_populates="plan")

    def __repr__(self):
        return f"<Plan(id={self.id}, goal_id={self.goal_id}, status={self.status})>"
```

---

### 2.4 任务表 (tasks)

**用途**: 存储从规划生成的任务

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 任务 ID | 1 |
| goal_id | INTEGER | FOREIGN KEY, NOT NULL | 目标 ID | 1 |
| plan_id | INTEGER | FOREIGN KEY, NULLABLE | 规划 ID | 1 |
| title | VARCHAR(200) | NOT NULL | 任务标题 | "安装 Python 环境" |
| description | TEXT | NULLABLE | 任务描述 | "下载并安装..." |
| estimated_hours | FLOAT | DEFAULT 0 | 预估工时 | 0.5 |
| due_date | DATETIME | NOT NULL | 截止时间 | "2026-01-27 10:00:00" |
| completed | BOOLEAN | DEFAULT FALSE | 是否完成 | False |
| completed_at | DATETIME | NULLABLE | 完成时间 | "2026-01-27 14:00:00" |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | "2026-01-27 10:00:00" |
| updated_at | DATETIME | NULLABLE | 更新时间 | "2026-01-27 14:00:00" |

**索引**:
```sql
CREATE INDEX idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX idx_tasks_plan_id ON tasks(plan_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_goal_date ON tasks(goal_id, due_date);
```

**外键关系**:
```sql
FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE SET NULL
```

**SQLAlchemy 模型**:
```python
# backend/app/models/task.py

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    estimated_hours = Column(Float, default=0)
    due_date = Column(DateTime, nullable=False, index=True)
    completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # 关系
    goal = relationship("Goal", back_populates="tasks")
    plan = relationship("Plan", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, completed={self.completed})>"
```

---

## 3. 数据库初始化

### 3.1 创建数据库表

```python
# backend/init_db.py

from app.core.database import engine, Base
from app.models import user, goal, plan, task

def init_db():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")

if __name__ == "__main__":
    init_db()
```

### 3.2 运行初始化

```bash
cd backend
python init_db.py
```

---

## 4. 数据库关系图

```
┌─────────────┐
│   users     │
├─────────────┤
│ id (PK)     │
│ username    │
│ password    │
│ email       │
│ created_at  │
└──────┬──────┘
       │ 1
       │ N
       │
       ↓
┌─────────────┐
│   goals     │
├─────────────┤
│ id (PK)     │
│ user_id (FK)│ ←┐
│ title       │  │ 1
│ description │  │ N
│ deadline    │  │
│ status      │  │
└──────┬──────┘  │
       │ 1       │
       │ N       │
       ↓         │
┌─────────────┐  │
│   plans     │  │
├─────────────┤  │
│ id (PK)     │  │
│ goal_id (FK)│──┘
│ content     │
│ status      │
└──────┬──────┘
       │ 1
       │ N
       │
       ↓
┌─────────────┐
│   tasks     │
├─────────────┤
│ id (PK)     │
│ goal_id (FK)│
│ plan_id (FK)│
│ title       │
│ due_date    │
│ completed   │
└─────────────┘
```

---

## 5. 数据迁移（未来使用）

### 5.1 使用 Alembic

**安装 Alembic**:
```bash
pip install alembic
```

**初始化 Alembic**:
```bash
cd backend
alembic init alembic
```

**配置 alembic.ini**:
```ini
sqlalchemy.url = sqlite:///./lifemanager.db
```

**生成迁移脚本**:
```bash
alembic revision --autogenerate -m "Initial migration"
```

**执行迁移**:
```bash
alembic upgrade head
```

---

## 6. 数据库性能优化

### 6.1 索引说明

**已添加的索引**:
- ✅ 用户表：username（唯一索引）
- ✅ 目标表：user_id, status, deadline
- ✅ 规划表：goal_id, status
- ✅ 任务表：goal_id, plan_id, due_date, completed

**复合索引**:
- ✅ 任务表：(goal_id, due_date) - 查询某个目标的任务时使用

### 6.2 查询优化建议

**避免 N+1 查询**:
```python
# ❌ 错误示例：N+1 查询
goals = db.query(Goal).all()
for goal in goals:
    print(goal.tasks)  # 每次循环都会执行一次查询

# ✅ 正确示例：使用 joinedload
from sqlalchemy.orm import joinedload
goals = db.query(Goal).options(joinedload(Goal.tasks)).all()
```

**使用索引查询**:
```python
# ✅ 使用索引字段查询
tasks = db.query(Task).filter(Task.goal_id == goal_id).all()
```

---

## 7. 数据安全

### 7.1 密码加密

使用 bcrypt 加密用户密码：

```python
import bcrypt

def hash_password(password: str) -> str:
    """加密密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

### 7.2 SQL 注入防护

使用 SQLAlchemy ORM 自动防护 SQL 注入，**不要使用原生 SQL**。

---

## 8. 数据备份

### 8.1 SQLite 备份

```bash
# 备份数据库
cp lifemanager.db lifemanager.db.backup

# 恢复数据库
cp lifemanager.db.backup lifemanager.db
```

### 8.2 定期备份脚本

```bash
# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /path/to/lifemanager.db /path/to/backups/lifemanager_$DATE.db
```

---

## 9. 常见问题

### Q1: 如何重置数据库？

```bash
cd backend
rm lifemanager.db
python init_db.py
```

### Q2: 如何查看数据库内容？

```bash
# 使用 SQLite 命令行
sqlite3 lifemanager.db

# SQLite 命令
.tables           # 查看所有表
.schema goals     # 查看表结构
SELECT * FROM goals;  # 查询数据
```

### Q3: 如何导出数据库为 SQL？

```bash
sqlite3 lifemanager.db .dump > backup.sql
```

---

## 10. 附录

### 10.1 完整数据库初始化脚本

```python
# backend/app/models/__init__.py

from .user import User
from .goal import Goal
from .plan import Plan
from .task import Task

__all__ = ["User", "Goal", "Plan", "Task"]
```

### 10.2 环境变量配置

```bash
# backend/.env
DATABASE_URL=sqlite:///./lifemanager.db
```

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-27 | v1.0 | 初始版本，完成数据库设计 |
