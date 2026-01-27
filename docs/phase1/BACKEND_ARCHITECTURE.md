# LifeManager MVP 后端架构设计文档

## 文档信息

- **版本**: v2.0
- **创建日期**: 2026-01-27
- **作者**: Python后端开发工程师 + 技术架构师
- **状态**: 已发布
- **适用阶段**: Phase 1 - MVP

---

## 1. 架构概述

### 1.1 架构选型

**采用架构**: **分层架构 (Layered Architecture)**

**选型理由**:
- ✅ 适合 MVP 阶段的快速开发
- ✅ 职责清晰，易于维护和测试
- ✅ 符合团队现有技能栈
- ✅ 支持未来扩展到微服务架构

### 1.2 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Frontend)                      │
│              (Vue3 + Uni-app / HBuilderX)               │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/REST API
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  - 接口定义 (Router)                               │  │
│  │  - 参数验证 (Pydantic)                             │  │
│  │  - 响应封装 (ApiResponse)                          │  │
│  │  - 认证授权 (Dependency Injection)                 │  │
│  └───────────────────┬───────────────────────────────┘  │
└──────────────────────┼───────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Services Layer (Business Logic)             │
│  ┌───────────────────────────────────────────────────┐  │
│  │  - AuthService  (认证业务)                       │  │
│  │  - GoalService  (目标业务)                       │  │
│  │  - PlanService  (规划业务)                       │  │
│  │  - TaskService  (任务业务)                       │  │
│  └───────────────────┬───────────────────────────────┘  │
└──────────────────────┼───────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌─────────────┐ ┌───────────┐ ┌──────────────┐
│  Core Layer │ │  Models   │ │  Utils Layer │
│             │ │ (ORM)     │ │              │
│ - AIService │ │ - User    │ │ - Logger     │
│ - AI Engine │ │ - Goal    │ │ - Validator  │
│ - Security  │ │ - Plan    │ │ - Timer      │
│ - Config    │ │ - Task    │ │ - FileOp     │
└─────────────┘ └───────────┘ └──────────────┘
       │              │
       ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐    │
│  │  SQLite     │  │  External AI │  │  Cache      │    │
│  │  Database   │  │  (DeepSeek)  │  │  (Future)   │    │
│  └─────────────┘  └──────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 分层架构详解

### 2.1 API Layer (`app/api/`)

**职责**:
- 定义 RESTful API 接口
- 请求参数验证（Pydantic）
- 响应数据封装
- 认证授权检查
- 调用 Services 层处理业务

**设计原则**:
- ✅ 轻量级，只负责接口层逻辑
- ✅ 不直接操作数据库，通过 Services 层
- ✅ 使用 FastAPI 的依赖注入
- ✅ 统一的异常处理

**目录结构**:
```
app/api/
├── __init__.py
├── auth.py          # 认证接口
├── goals.py         # 目标接口
├── plans.py         # 规划接口
└── tasks.py         # 任务接口
```

**代码示例**:
```python
# app/api/goals.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.response import ApiResponse
from app.models.user import User
from app.services.goal_service import GoalService
from app.schemas.goal import GoalCreate, GoalResponse

router = APIRouter(prefix="/api/goals", tags=["goals"])

@router.post("/", response_model=ApiResponse[GoalResponse])
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建目标
    
    - **title**: 目标标题
    - **description**: 目标描述
    - **deadline**: 截止日期
    """
    try:
        goal_service = GoalService(db)
        goal = goal_service.create_goal(current_user.id, goal_data)
        
        return ApiResponse.success(
            data=goal,
            message="目标创建成功"
        )
    except Exception as e:
        return ApiResponse.error(
            code=2002,
            message=str(e)
        )
```

---

### 2.2 Services Layer (`app/services/`)

**职责**:
- 封装业务逻辑
- 数据组装和转换
- 事务管理
- 调用 Core 层和 Models
- 跨模块的业务编排

**设计原则**:
- ✅ 单一职责，每个 Service 负责一个业务模块
- ✅ 无状态，可水平扩展
- ✅ 统一错误处理和日志记录
- ✅ 使用 DTO 模式进行数据传输

**目录结构**:
```
app/services/
├── __init__.py
├── auth_service.py     # 认证业务逻辑
├── goal_service.py     # 目标业务逻辑
├── plan_service.py     # 规划业务逻辑
└── task_service.py     # 任务业务逻辑
```

**代码示例**:
```python
# app/services/plan_service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.plan import Plan
from app.models.goal import Goal
from app.schemas.plan import PlanCreate, PlanUpdate
from app.core.ai_engine import AIEngine
from app.core.exceptions import PlanNotFoundError, GoalNotFoundError

class PlanService:
    """规划业务逻辑服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_engine = AIEngine()
    
    def generate_plan(
        self, 
        user_id: int, 
        goal_id: int, 
        available_hours: int = 2
    ) -> Plan:
        """
        生成规划
        
        Args:
            user_id: 用户 ID
            goal_id: 目标 ID
            available_hours: 每天可用小时数
            
        Returns:
            规划对象
            
        Raises:
            GoalNotFoundError: 目标不存在
            Exception: AI 生成失败
        """
        # 1. 查询目标
        goal = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).first()
        
        if not goal:
            logger.warning(f"目标不存在: goal_id={goal_id}, user_id={user_id}")
            raise GoalNotFoundError()
        
        # 2. 调用 AI 生成规划
        try:
            plan_content = self.ai_engine.generate_plan(
                goal_title=goal.title,
                goal_description=goal.description or "",
                deadline=goal.deadline.strftime("%Y-%m-%d") if goal.deadline else "",
                available_hours=available_hours
            )
            
            logger.info(f"AI 规划生成成功: goal_id={goal_id}")
            
        except Exception as e:
            logger.error(f"AI 规划生成失败: {e}")
            raise Exception(f"AI 生成失败: {str(e)}")
        
        # 3. 创建规划记录
        plan = Plan(
            goal_id=goal_id,
            content=plan_content,
            status="draft",
            total_stages=len(plan_content.get("stages", [])),
            total_tasks=sum(len(stage.get("tasks", [])) for stage in plan_content.get("stages", [])),
            estimated_total_hours=sum(
                task.get("estimated_hours", 0)
                for stage in plan_content.get("stages", [])
                for task in stage.get("tasks", [])
            )
        )
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return plan
    
    def confirm_plan(self, user_id: int, plan_id: int) -> Plan:
        """
        确认规划
        
        Args:
            user_id: 用户 ID
            plan_id: 规划 ID
            
        Returns:
            更新后的规划对象
        """
        # 查询规划
        plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
        
        if not plan:
            raise PlanNotFoundError()
        
        # 更新状态
        plan.status = "confirmed"
        self.db.commit()
        
        # 异步创建任务（使用 TaskService）
        from app.services.task_service import TaskService
        task_service = TaskService(self.db)
        task_service.create_tasks_from_plan(plan, available_hours=2)
        
        logger.info(f"规划确认成功: plan_id={plan_id}")
        
        return plan
```

---

### 2.3 Core Layer (`app/core/`)

**职责**:
- 核心算法实现（如 AI 调用逻辑）
- 配置管理
- 安全工具（密码加密、JWT）
- 数据库连接管理
- 抽象基类定义

**目录结构**:
```
app/core/
├── __init__.py
├── config.py           # 配置管理
├── database.py         # 数据库连接
├── security.py         # 安全工具（JWT、密码加密）
├── ai_engine.py        # AI 引擎（调用 DeepSeek）
├── dependencies.py     # FastAPI 依赖
├── exceptions.py       # 自定义异常
└── response.py         # 统一响应格式
```

**AI 引擎设计**:
```python
# app/core/ai_engine.py

import os
import json
from typing import Dict, Any
from openai import OpenAI
from loguru import logger

from app.core.config import settings

class AIEngine:
    """AI 规划生成引擎"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
        )
        self.model = os.getenv("AI_MODEL", "deepseek-chat")
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", 4000))
        self.temperature = float(os.getenv("AI_TEMPERATURE", 0.7))
    
    def generate_plan(
        self,
        goal_title: str,
        goal_description: str,
        deadline: str,
        available_hours: int
    ) -> Dict[str, Any]:
        """
        生成规划
        
        Args:
            goal_title: 目标标题
            goal_description: 目标描述
            deadline: 截止日期
            available_hours: 每天可用小时数
            
        Returns:
            规划 JSON 数据
            
        Raises:
            ValueError: AI 返回格式错误
            Exception: AI 调用失败
        """
        # 构造 Prompt
        prompt = self._build_prompt(goal_title, goal_description, deadline, available_hours)
        
        try:
            logger.info(f"调用 AI 生成规划: {goal_title}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}  # 强制返回 JSON
            )
            
            content = response.choices[0].message.content
            plan_data = json.loads(content)
            
            # 验证数据格式
            self._validate_plan_data(plan_data)
            
            logger.info(f"规划生成成功: {len(plan_data.get('stages', []))} 个阶段")
            
            return plan_data
            
        except json.JSONDecodeError as e:
            logger.error(f"AI 返回的 JSON 格式错误: {e}")
            raise ValueError("AI 返回格式错误，请重试")
        except Exception as e:
            logger.error(f"AI 调用失败: {e}")
            raise Exception(f"AI 服务不可用: {str(e)}")
    
    def _build_prompt(self, goal_title: str, goal_description: str, 
                     deadline: str, available_hours: int) -> str:
        """构造 Prompt"""
        return f"""
请根据以下信息，生成一个详细的执行规划：

## 目标信息
- 目标名称：{goal_title}
- 目标描述：{goal_description}
- 期望完成时间：{deadline}
- 每天可用时间：约 {available_hours} 小时

## 要求
1. 将目标分解为 3-5 个阶段（按时间顺序）
2. 每个阶段分解为 3-8 个具体任务
3. 估算每个任务的预估时间（小时）
4. 任务之间有合理的逻辑依赖
5. 考虑学习曲线和难度递增

## 输出格式
请严格按照以下 JSON 格式输出（不要添加其他文字）：

{{
  "stages": [
    {{
      "name": "阶段名称",
      "order": 1,
      "description": "阶段描述（可选）",
      "tasks": [
        {{
          "title": "任务标题",
          "description": "任务描述（可选）",
          "estimated_hours": 2.0,
          "order": 1
        }}
      ]
    }}
  ]
}}
"""
    
    SYSTEM_PROMPT = """
你是一个专业的目标规划助手，擅长将长期目标分解为可执行的短期任务。

你的任务：
1. 分析用户的目标和约束条件
2. 将目标分解为 3-5 个阶段
3. 每个阶段分解为具体的任务
4. 估算每个任务的时间（小时）
5. 确保任务之间的逻辑顺序合理

输出要求：
1. 必须返回标准的 JSON 格式
2. 阶段数量：3-5 个
3. 每个阶段任务数：3-8 个
4. 任务描述简洁明确
5. 时间估算合理（不要太乐观）
"""
    
    def _validate_plan_data(self, plan_data: Dict[str, Any]):
        """验证规划数据格式"""
        if not isinstance(plan_data, dict):
            raise ValueError("规划数据必须是字典")
        
        if "stages" not in plan_data:
            raise ValueError("规划数据缺少 stages 字段")
        
        stages = plan_data["stages"]
        if not isinstance(stages, list) or len(stages) == 0:
            raise ValueError("stages 必须是非空列表")
        
        if len(stages) < 2 or len(stages) > 6:
            raise ValueError("阶段数量应在 2-6 个之间")
        
        for i, stage in enumerate(stages):
            if "name" not in stage or "tasks" not in stage:
                raise ValueError(f"阶段 {i+1} 缺少必要字段")
            
            tasks = stage["tasks"]
            if not isinstance(tasks, list) or len(tasks) == 0:
                raise ValueError(f"阶段 {i+1} 的任务列表为空")
            
            for j, task in enumerate(tasks):
                if "title" not in task or "estimated_hours" not in task:
                    raise ValueError(f"阶段 {i+1} 任务 {j+1} 缺少必要字段")
                
                if not isinstance(task["estimated_hours"], (int, float)):
                    raise ValueError(f"任务 {j+1} 的 estimated_hours 必须是数字")


# 全局实例
ai_engine = AIEngine()
```

---

### 2.4 Utils Layer (`app/utils/`)

**职责**:
- 通用工具类
- 日志配置
- 数据验证器
- 性能监控工具

**目录结构**:
```
app/utils/
├── __init__.py
├── logger.py           # 日志配置
├── validators.py       # 数据验证器
└── timer.py            # 性能计时器
```

**日志配置**:
```python
# app/utils/logger.py

import sys
from loguru import logger
from app.core.config import settings

def setup_logger():
    """配置日志系统"""
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # 文件输出
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="200 MB",
        retention="30 days",
        compression="zip"
    )
    
    # 错误日志单独文件
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="100 MB",
        retention="60 days",
        compression="zip"
    )
    
    return logger

# 初始化日志
logger = setup_logger()
```

---

### 2.5 Models Layer (`app/models/`)

**职责**:
- 定义 SQLAlchemy ORM 模型
- 数据库表结构映射
- 模型之间的关系定义

**目录结构**:
```
app/models/
├── __init__.py
├── user.py             # 用户模型
├── goal.py             # 目标模型
├── plan.py             # 规划模型
└── task.py             # 任务模型
```

---

## 3. 设计模式应用

### 3.1 依赖注入 (Dependency Injection)

FastAPI 自带的依赖注入系统：

```python
# app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    
    使用依赖注入，任何需要认证的接口只需添加此参数即可
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解码 Token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # 获取 user_id
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user
```

**使用示例**:
```python
@router.post("/goals")
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),                          # 依赖注入：数据库会话
    current_user: User = Depends(get_current_user)         # 依赖注入：当前用户
):
    # 业务逻辑
    pass
```

---

### 3.2 DTO 模式 (Data Transfer Object)

使用 Pydantic 定义请求和响应模型：

```python
# app/schemas/goal.py

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

class GoalCreate(BaseModel):
    """创建目标请求"""
    title: str = Field(..., min_length=1, max_length=200, description="目标标题")
    description: Optional[str] = Field(None, max_length=1000, description="目标描述")
    deadline: Optional[date] = Field(None, description="截止日期")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('标题不能为空')
        return v.strip()

class GoalResponse(BaseModel):
    """目标响应"""
    id: int
    title: str
    description: Optional[str]
    deadline: Optional[date]
    status: str
    created_at: str
    
    class Config:
        from_attributes = True  # 支持从 ORM 模型转换
```

---

### 3.3 统一响应格式

```python
# app/core/response.py

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""
    code: int = Field(0, description="响应码，0 表示成功")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    
    @classmethod
    def success(cls, data: T = None, message: str = "success"):
        """成功响应"""
        return cls(code=0, message=message, data=data)
    
    @classmethod
    def error(cls, code: int = 1, message: str = "error", data: T = None):
        """错误响应"""
        return cls(code=code, message=message, data=data)
```

**使用示例**:
```python
# 成功响应
return ApiResponse.success(data=goal, message="目标创建成功")

# 错误响应
return ApiResponse.error(code=2001, message="目标不存在")
```

---

## 4. 认证方式设计

### 4.1 认证方式：用户名 + 密码

**设计理由**:
1. **简单直接**: 适合 MVP 阶段，开发成本低
2. **文档一致性**: 与 API 文档设计保持一致
3. **用户友好**: 用户名比手机号更灵活，无需验证码
4. **隐私友好**: 不需要收集手机号等敏感信息

### 4.2 认证流程

```
┌─────────┐                    ┌─────────┐
│ Client  │                    │ Server  │
└────┬────┘                    └────┬────┘
     │                              │
     │ 1. POST /api/auth/register  │
     │    {username, password,     │
     │     email}                  │
     ├─────────────────────────────>│
     │                              │
     │                              │ 2. 检查用户名是否存在
     │                              │ 3. 加密密码 (bcrypt)
     │                              │ 4. 创建用户
     │                              │ 5. 生成 JWT Token
     │                              │
     │ 6. {token, user_id}         │
     │<─────────────────────────────┤
     │                              │
     │ 7. 保存 Token               │
     │                              │
     │ 8. GET /api/goals           │
     │    Header: Authorization:   │
     │      Bearer {token}         │
     ├─────────────────────────────>│
     │                              │
     │                              │ 9. 验证 JWT Token
     │                              │ 10. 提取 user_id
     │                              │ 11. 查询用户数据
     │                              │
     │ 12. {code: 0, data: goals} │
     │<─────────────────────────────┤
```

### 4.3 JWT Token 设计

**Token 结构**:
```json
{
  "sub": "123",                    // user_id
  "exp": 1738540800,               // 过期时间（7天后）
  "iat": 1737936000                // 签发时间
}
```

**配置**:
```python
# .env
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60*24*7  # 7 天
```

---

## 5. 错误处理设计

### 5.1 错误码定义

```python
# app/core/exceptions.py

class AppException(Exception):
    """应用异常基类"""
    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)

# 认证错误
class UserExistsError(AppException):
    def __init__(self, message: str = "用户名已存在"):
        super().__init__(code=1001, message=message)

class UserNotFoundError(AppException):
    def __init__(self, message: str = "用户不存在"):
        super().__init__(code=1003, message=message)

class PasswordError(AppException):
    def __init__(self, message: str = "密码错误"):
        super().__init__(code=1004, message=message)

# 目标错误
class GoalNotFoundError(AppException):
    def __init__(self, message: str = "目标不存在"):
        super().__init__(code=2001, message=message)

class GoalNotBelongToUserError(AppException):
    def __init__(self, message: str = "目标不属于当前用户"):
        super().__init__(code=2002, message=message)

# 规划错误
class PlanNotFoundError(AppException):
    def __init__(self, message: str = "规划不存在"):
        super().__init__(code=3001, message=message)

class PlanAlreadyConfirmedError(AppException):
    def __init__(self, message: str = "规划已确认，无法修改"):
        super().__init__(code=3002, message=message)

# 任务错误
class TaskNotFoundError(AppException):
    def __init__(self, message: str = "任务不存在"):
        super().__init__(code=4001, message=message)

# AI 错误
class AIServiceUnavailableError(AppException):
    def __init__(self, message: str = "AI 服务不可用，请稍后重试"):
        super().__init__(code=4002, message=message)

class AIGenerationFailedError(AppException):
    def __init__(self, message: str = "AI 生成失败"):
        super().__init__(code=4003, message=message)
```

### 5.2 全局异常处理

```python
# app/core/middleware.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import AppException
from app.core.response import ApiResponse

async def app_exception_handler(request: Request, exc: AppException):
    """自定义异常处理器"""
    logger.error(f"业务异常: {exc.code} - {exc.message}")
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse.error(code=exc.code, message=exc.message).model_dump()
    )

async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未知异常: {type(exc).__name__} - {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            code=1,
            message="服务器内部错误，请稍后重试"
        ).model_dump()
    )
```

**注册异常处理器**:
```python
# main.py

from app.core.exceptions import AppException
from app.core.middleware import app_exception_handler, general_exception_handler

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

---

## 6. 配置管理

### 6.1 环境变量配置

```python
# app/core/config.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME: str = "LifeManager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./lifemanager.db"
    
    # OpenAI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.deepseek.com"
    AI_MODEL: str = "deepseek-chat"
    AI_MAX_TOKENS: int = 4000
    AI_TEMPERATURE: float = 0.7
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()
```

---

## 7. 性能优化建议

### 7.1 数据库优化

```python
# 使用索引查询
from sqlalchemy import or_

# ✅ 好的做法：使用索引字段
goals = db.query(Goal).filter(Goal.user_id == user_id).all()

# ❌ 不好的做法：避免全表扫描
goals = db.query(Goal).filter(Goal.title.contains("Python")).all()
```

### 7.2 避免N+1查询

```python
from sqlalchemy.orm import joinedload

# ❌ N+1 查询
goals = db.query(Goal).all()
for goal in goals:
    print(goal.tasks)  # 每次循环都执行一次查询

# ✅ 使用 joinedload 预加载
goals = db.query(Goal).options(joinedload(Goal.tasks)).all()
for goal in goals:
    print(goal.tasks)  # 不会额外查询
```

### 7.3 使用缓存

```python
from functools import wraps
import time

def timed_cache(seconds: int = 300):
    """带过期时间的缓存装饰器"""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator
```

---

## 8. 安全最佳实践

### 8.1 密码加密

```python
# 使用 bcrypt 加密
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 8.2 SQL注入防护

```python
# ✅ 使用 SQLAlchemy ORM，自动防护 SQL 注入
user = db.query(User).filter(User.username == username).first()

# ❌ 不要使用原生 SQL
# db.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

---

## 9. 部署架构

### 9.1 开发环境

```
Frontend (HBuilderX) → Backend (FastAPI) → SQLite Database
```

### 9.2 生产环境（未来）

```
                    ┌─────────────┐
                    │   Nginx     │ (反向代理)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   FastAPI   │ (多实例)
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      ┌─────────┐    ┌─────────┐    ┌─────────┐
      │  Redis  │    │PostgreSQL│   │ DeepSeek│
      │ (Cache) │    │(Database)│   │   API   │
      └─────────┘    └─────────┘    └─────────┘
```

---

## 10. 总结

### 10.1 架构优势

- ✅ **职责清晰**: 四层架构，每层职责明确
- ✅ **易于测试**: 无状态服务，依赖注入
- ✅ **可扩展性**: 支持水平扩展和垂直扩展
- ✅ **安全可靠**: JWT 认证，密码加密，SQL注入防护
- ✅ **开发效率**: 统一响应格式，统一错误处理

### 10.2 后续优化方向

1. **缓存层**: 添加 Redis 缓存
2. **异步任务**: 使用 Celery 处理耗时任务
3. **消息队列**: 使用 RabbitMQ/Kafka 解耦服务
4. **监控告警**: 集成 Prometheus + Grafana
5. **日志聚合**: 使用 ELK Stack

---

**文档版本**: v2.0  
**最后更新**: 2026-01-27  
**审核状态**: ✅ 已通过 Python后端开发工程师和技术架构师审核
