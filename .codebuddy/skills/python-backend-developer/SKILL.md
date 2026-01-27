---
name: Python后端开发工程师
description: 专业的Python后端开发专家,精通Python后端技术栈(FastAPI/Flask/Django)、数据库操作、API设计、微服务架构。适用于后端服务开发、API设计、数据处理、系统架构等后端开发场景。
---

# Python后端开发工程师技能

## 概述

本技能提供专业的Python后端开发能力,涵盖从API设计到系统架构的全流程。帮助快速构建高性能、可扩展、安全可靠的Python后端服务。

## 技术栈

### Web框架
- **FastAPI**: 现代高性能Web框架,自动API文档
- **Flask**: 轻量级微框架,灵活可扩展
- **Django**: 全功能框架,快速开发企业应用

### 数据库
- **关系型数据库**: PostgreSQL, MySQL, SQLite
- **NoSQL**: MongoDB, Redis
- **ORM**: SQLAlchemy, Tortoise ORM, Django ORM

### 其他技术
- **异步编程**: asyncio, aiohttp
- **认证授权**: JWT, OAuth2, RBAC
- **任务队列**: Celery, RQ
- **消息队列**: RabbitMQ, Kafka
- **容器化**: Docker, Docker Compose
- **测试**: pytest, unittest

## 核心能力

### 1. Web框架使用

#### FastAPI快速入门

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="My API",
    description="API Documentation",
    version="1.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

# 路由
@app.get("/", tags=["Health"])
async def root():
    return {"message": "API is running"}

@app.post("/users/", response_model=UserResponse, tags=["Users"])
async def create_user(user: UserCreate):
    """创建新用户"""
    # 业务逻辑
    return user

@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: int):
    """获取用户信息"""
    if user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    return {"id": user_id, "username": "test", "email": "test@example.com", "is_active": True}

@app.get("/users/", response_model=List[UserResponse], tags=["Users"])
async def list_users(skip: int = 0, limit: int = 10):
    """获取用户列表"""
    return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Flask快速入门

```python
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)

# 认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        # 验证token逻辑
        return f(*args, **kwargs)
    return decorated

@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return jsonify({
        'users': [],
        'total': 0,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # 创建用户逻辑
    return jsonify({'message': 'User created'}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 2. 数据库操作

#### SQLAlchemy使用

```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# crud.py
from sqlalchemy.orm import Session
from typing import Optional, List
from models import User

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: dict) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        for key, value in user_update.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
```

#### MongoDB使用

```python
# db.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient("mongodb://localhost:27017")

async def close_mongo():
    global client
    if client:
        client.close()

def get_db():
    return client.mydatabase

# repository.py
from bson import ObjectId
from datetime import datetime

class UserRepository:
    def __init__(self, db):
        self.collection = db.users
    
    async def create(self, user_data: dict) -> str:
        user_data['created_at'] = datetime.utcnow()
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    async def get_by_id(self, user_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(user_id)})
    
    async def get_by_email(self, email: str) -> Optional[dict]:
        return await self.collection.find_one({"email": email})
    
    async def update(self, user_id: str, update_data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
```

### 3. 认证授权

#### JWT认证

```python
# auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": user_id}

# 路由中使用
@app.post("/login")
async def login(username: str, password: str):
    # 验证用户
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}
```

### 4. 异步编程

#### asyncio使用

```python
import asyncio
import aiohttp

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_multiple_requests(urls: list) -> list:
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# FastAPI异步路由
@app.get("/async-data")
async def get_async_data():
    data = await fetch_data("https://api.example.com/data")
    return data

# 异步数据库操作
@app.get("/users/{user_id}")
async def get_user_async(user_id: int):
    async with get_db() as db:
        user = await db.execute(
            select(User).where(User.id == user_id)
        )
        return user.scalar_one_or_none()
```

### 5. 任务队列

#### Celery配置

```python
# celery_app.py
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
)

# tasks.py
from celery_app import celery_app

@celery_app.task
def send_email(to: str, subject: str, body: str) -> bool:
    """发送邮件任务"""
    # 发送邮件逻辑
    return True

@celery_app.task
def process_data(data_id: int) -> dict:
    """处理数据任务"""
    # 处理逻辑
    return {"status": "completed", "data_id": data_id}

# 在FastAPI中使用
@app.post("/send-email")
async def trigger_email(email: str, subject: str, body: str):
    send_email.delay(email, subject, body)
    return {"message": "Email task queued"}
```

### 6. API设计原则

#### RESTful API设计
- 使用HTTP方法语义(GET/POST/PUT/DELETE)
- 使用合理的资源命名(复数形式)
- 使用HTTP状态码表示结果
- 实现分页、排序、过滤
- 版本控制(/api/v1/)

#### API响应格式

```python
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class APIResponse(Generic[T]):
    def __init__(self, code: int = 200, message: str = "Success", data: Optional[T] = None):
        self.code = code
        self.message = message
        self.data = data
    
    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }

class PaginatedResponse(APIResponse[list]):
    def __init__(self, items: list, total: int, page: int, per_page: int):
        super().__init__(data=items)
        self.total = total
        self.page = page
        self.per_page = per_page
        self.total_pages = (total + per_page - 1) // per_page
    
    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "data": {
                "items": self.data,
                "total": self.total,
                "page": self.page,
                "per_page": self.per_page,
                "total_pages": self.total_pages
            }
        }

# 使用示例
@app.get("/users")
async def list_users(page: int = 1, per_page: int = 10):
    users = get_users(page, per_page)
    total = count_users()
    return PaginatedResponse(users, total, page, per_page).to_dict()
```

### 7. 错误处理和日志

#### 全局异常处理

```python
# exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        logger.error(f"API Exception: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={"code": exc.code, "message": exc.message}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "Validation failed",
                "errors": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "Internal server error"}
        )

# 日志配置
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 8. 配置管理

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "My API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# 使用
settings = get_settings()
print(settings.DATABASE_URL)
```

### 9. 测试

#### pytest测试示例

```python
# tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200

def test_invalid_user():
    response = client.get("/users/999")
    assert response.status_code == 404

# 使用pytest fixtures
@pytest.fixture
def db_session():
    # 创建测试数据库会话
    session = TestSession()
    try:
        yield session
    finally:
        session.close()

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### 10. 性能优化

```python
# 缓存装饰器
from functools import wraps
import json
import hashlib

def cache_result(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            key = hashlib.md5(
                json.dumps((args, kwargs)).encode()
            ).hexdigest()
            
            # 检查缓存
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 设置缓存
            await redis.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# 数据库连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 查询优化
from sqlalchemy.orm import selectinload

def get_users_with_posts(db: Session):
    return db.query(User).options(
        selectinload(User.posts)
    ).all()
```

## 项目结构推荐

```
project/
├── app/
│   ├── api/              # API路由
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── users.py
│   │   │   │   └── posts.py
│   │   │   └── api.py
│   ├── core/             # 核心配置
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── crud/             # 数据库操作
│   │   ├── user.py
│   │   └── post.py
│   ├── models/           # 数据模型
│   │   ├── user.py
│   │   └── post.py
│   ├── schemas/          # Pydantic模型
│   │   ├── user.py
│   │   └── post.py
│   ├── services/         # 业务逻辑
│   │   ├── user_service.py
│   │   └── auth_service.py
│   ├── utils/            # 工具函数
│   │   ├── db.py
│   │   └── helpers.py
│   └── main.py
├── tests/                # 测试
│   ├── test_api/
│   ├── test_crud/
│   └── conftest.py
├── alembic/              # 数据库迁移
├── requirements.txt
├── .env
└── README.md
```

## 安全最佳实践

- 使用HTTPS传输
- 密码使用bcrypt加密
- JWT Token设置合理过期时间
- 实现请求限流(Rate Limiting)
- 输入验证和SQL注入防护
- CORS配置合理
- 敏感信息不记录日志
- 定期更新依赖包

## 部署

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

## 使用说明

### 何时使用本技能
- 需要开发Python后端API
- 需要设计数据库模型和API接口
- 需要实现认证授权
- 需要优化后端性能
- 需要编写后端测试
- 需要部署后端服务

### 如何有效使用
1. 明确技术栈选型(FastAPI/Flask/Django)
2. 提供需求文档和API规范
3. 说明数据库设计和数据模型
4. 明确认证和权限要求
5. 保持沟通,及时反馈调整

## 质量检查清单

在交付代码前确认:
- [ ] 代码符合PEP8规范
- [ ] 类型提示完整
- [ ] 异常处理完善
- [ ] 日志记录合理
- [ ] 数据库查询优化
- [ ] 安全措施到位
- [ ] 单元测试覆盖核心逻辑
- [ ] API文档完整
- [ ] 配置管理规范
