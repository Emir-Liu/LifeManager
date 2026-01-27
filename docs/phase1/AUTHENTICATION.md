# LifeManager MVP 认证授权文档

## 文档信息

- **版本**: v1.0
- **创建日期**: 2026-01-27
- **作者**: 产品经理
- **状态**: 已发布
- **适用阶段**: Phase 1 - MVP

---

## 1. 认证方案概述

### 1.1 认证方式

**采用方案**: JWT (JSON Web Token) Bearer Token 认证

**选型理由**:
- ✅ 无状态，适合前后端分离架构
- ✅ 跨域支持友好
- ✅ 移动端支持良好
- ✅ 可扩展性好

### 1.2 认证流程

```
用户注册/登录
    ↓
服务器验证凭据
    ↓
生成 JWT Token
    ↓
返回 Token 给客户端
    ↓
客户端存储 Token
    ↓
后续请求携带 Token
    ↓
服务器验证 Token
    ↓
允许访问受保护资源
```

---

## 2. JWT 配置

### 2.1 环境变量

```bash
# backend/.env
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60*24*7  # 7 天
```

**安全注意事项**:
- 🔒 JWT_SECRET_KEY 必须保密
- 🔒 生产环境使用强密钥（至少 32 字符）
- 🔒 定期轮换密钥

### 2.2 JWT 工具类

```python
# backend/app/core/security.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 Access Token

    Args:
        data: 要编码的数据（通常是 user_id）
        expires_delta: 过期时间增量

    Returns:
        JWT Token 字符串
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 Access Token

    Args:
        token: JWT Token 字符串

    Returns:
        解码后的数据字典

    Raises:
        JWTError: Token 无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

---

## 3. 认证中间件

### 3.1 获取当前用户

```python
# backend/app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户

    Args:
        token: JWT Token
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 认证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码 Token
    payload = decode_access_token(token)
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

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前激活用户（可扩展状态检查）
    """
    return current_user
```

### 3.2 使用示例

```python
# backend/app/api/goals.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/goals", tags=["goals"])

@router.get("/")
async def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的目标列表"""
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    return {"code": 0, "message": "success", "data": goals}
```

---

## 4. 认证接口实现

### 4.1 用户注册

```python
# backend/app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str
    password: str
    email: Optional[EmailStr] = None

    @validator('username')
    def validate_username(cls, v):
        if not (3 <= len(v) <= 20):
            raise ValueError('用户名长度必须在 3-20 个字符之间')
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少 6 个字符')
        return v

@router.post("/register")
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """用户注册"""

    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 1001, "message": "用户名已存在"}
        )

    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": 1002, "message": "邮箱已被注册"}
            )

    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 生成 Token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "code": 0,
        "message": "注册成功",
        "data": {
            "user_id": new_user.id,
            "username": new_user.username,
            "token": access_token
        }
    }
```

### 4.2 用户登录

```python
class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str
    password: str

@router.post("/login")
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录"""

    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 1003, "message": "用户名或密码错误"}
        )

    # 验证密码
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 1004, "message": "用户名或密码错误"}
        )

    # 生成 Token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "code": 0,
        "message": "登录成功",
        "data": {
            "user_id": user.id,
            "username": user.username,
            "token": access_token
        }
    }
```

### 4.3 用户登出

```python
@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    用户登出

    说明：由于 JWT 是无状态的，服务端无法主动作废 Token。
    客户端只需删除本地存储的 Token 即可。
    """
    return {
        "code": 0,
        "message": "登出成功",
        "data": None
    }
```

---

## 5. 前端认证实现

### 5.1 Token 存储与获取

```javascript
// frontend/utils/storage.js

const TOKEN_KEY = 'lifemanager_token'
const USER_KEY = 'lifemanager_user'

export const storage = {
  // 保存 Token
  setToken(token) {
    uni.setStorageSync(TOKEN_KEY, token)
  },

  // 获取 Token
  getToken() {
    return uni.getStorageSync(TOKEN_KEY) || ''
  },

  // 删除 Token
  removeToken() {
    uni.removeStorageSync(TOKEN_KEY)
  },

  // 保存用户信息
  setUser(user) {
    uni.setStorageSync(USER_KEY, JSON.stringify(user))
  },

  // 获取用户信息
  getUser() {
    const userStr = uni.getStorageSync(USER_KEY)
    return userStr ? JSON.parse(userStr) : null
  },

  // 删除用户信息
  removeUser() {
    uni.removeStorageSync(USER_KEY)
  },

  // 清除所有认证信息
  clearAuth() {
    this.removeToken()
    this.removeUser()
  }
}
```

### 5.2 请求拦截器

```javascript
// frontend/utils/request.js

import { storage } from './storage.js'

const BASE_URL = 'http://localhost:8000/api'

// 创建请求拦截器
const request = (options) => {
  return new Promise((resolve, reject) => {
    // 添加 Token
    const token = storage.getToken()
    const header = {
      'Content-Type': 'application/json',
      ...options.header
    }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    // 发起请求
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header,
      success: (res) => {
        if (res.statusCode === 200) {
          const { code, message, data } = res.data

          if (code === 0) {
            resolve(data)
          } else if (code === 1003 || code === 1004) {
            // 认证失败，跳转到登录页
            storage.clearAuth()
            uni.reLaunch({
              url: '/pages/login/login'
            })
            reject(new Error(message))
          } else {
            uni.showToast({
              title: message || '请求失败',
              icon: 'none'
            })
            reject(new Error(message))
          }
        } else {
          reject(new Error('网络请求失败'))
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络连接失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// 封装常用方法
export const get = (url, data = {}, options = {}) => {
  return request({
    url,
    method: 'GET',
    data,
    ...options
  })
}

export const post = (url, data = {}, options = {}) => {
  return request({
    url,
    method: 'POST',
    data,
    ...options
  })
}

export const put = (url, data = {}, options = {}) => {
  return request({
    url,
    method: 'PUT',
    data,
    ...options
  })
}

export const del = (url, data = {}, options = {}) => {
  return request({
    url,
    method: 'DELETE',
    data,
    ...options
  })
}
```

### 5.3 Vuex 状态管理

```javascript
// frontend/store/modules/user.js

import { storage } from '@/utils/storage.js'

const state = {
  token: storage.getToken(),
  userInfo: storage.getUser()
}

const getters = {
  isLogin: state => !!state.token,
  username: state => state.userInfo?.username || ''
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    storage.setToken(token)
  },

  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo
    storage.setUser(userInfo)
  },

  CLEAR_AUTH(state) {
    state.token = ''
    state.userInfo = null
    storage.clearAuth()
  }
}

const actions = {
  // 登录
  async login({ commit }, { username, password }) {
    const res = await post('/auth/login', { username, password })

    commit('SET_TOKEN', res.token)
    commit('SET_USER_INFO', {
      user_id: res.user_id,
      username: res.username
    })

    return res
  },

  // 注册
  async register({ commit }, { username, password, email }) {
    const res = await post('/auth/register', { username, password, email })

    commit('SET_TOKEN', res.token)
    commit('SET_USER_INFO', {
      user_id: res.user_id,
      username: res.username
    })

    return res
  },

  // 登出
  logout({ commit }) {
    commit('CLEAR_AUTH')
    uni.reLaunch({
      url: '/pages/index/index'
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
```

---

## 6. 安全最佳实践

### 6.1 密码安全

```python
# ✅ 正确：使用 bcrypt 加密
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash(password)

# ❌ 错误：不要使用 MD5 或 SHA1
# import hashlib
# hashed = hashlib.md5(password.encode()).hexdigest()  # 不安全！
```

### 6.2 Token 安全

```python
# ✅ 正确：Token 存储在 HttpOnly Cookie 中（可选）
# from fastapi import Response
# response.set_cookie(
#     key="access_token",
#     value=token,
#     httponly=True,
#     secure=True,  # HTTPS only
#     samesite="lax"
# )

# ⚠️ 注意：Uni-app 中 Token 存储在本地存储中
# 生产环境建议使用 HTTPS，防止中间人攻击
```

### 6.3 防止暴力破解

```python
# 添加速率限制（可选）
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 每分钟最多 5 次请求
async def login(...):
    pass
```

---

## 7. 错误码说明

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| 0 | 成功 | 200 |
| 1001 | 用户名已存在 | 400 |
| 1002 | 邮箱已被注册 | 400 |
| 1003 | 用户不存在 | 401 |
| 1004 | 密码错误 | 401 |
| 1005 | Token 无效或过期 | 401 |

---

## 8. 测试

### 8.1 注册测试

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
  }'
```

### 8.2 登录测试

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 8.3 受保护接口测试

```bash
# 使用返回的 token
TOKEN="your-jwt-token-here"

curl -X GET http://localhost:8000/api/goals \
  -H "Authorization: Bearer $TOKEN"
```

---

## 9. 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-27 | v1.0 | 初始版本，完成认证设计 |
