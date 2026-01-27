"""
认证相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.response import success_response, error_response
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()


@router.post("/login")
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码
    """
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        logger.warning(f"登录失败: 用户不存在 - {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(user_data.password, user.password_hash):
        logger.warning(f"登录失败: 密码错误 - {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查用户是否激活
    if not user.is_active:
        logger.warning(f"登录失败: 用户未激活 - {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 生成令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info(f"用户登录成功: {user.username}")

    return success_response(
        data={
            "user_id": user.id,
            "username": user.username,
            "token": access_token,
            "refresh_token": refresh_token
        },
        message="登录成功"
    )


@router.post("/register")
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **username**: 用户名
    - **password**: 密码
    - **email**: 邮箱（可选）
    """
    # 检查用户名是否已注册
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        logger.warning(f"注册失败: 用户名已存在 - {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已注册"
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

    # 生成令牌
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    logger.info(f"新用户注册成功: {new_user.username}")

    return success_response(
        data={
            "user_id": new_user.id,
            "username": new_user.username,
            "token": access_token,
            "refresh_token": refresh_token
        },
        message="注册成功"
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌

    - **refresh_token**: 刷新令牌
    """
    # 解码刷新令牌
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        logger.warning("令牌刷新失败: 无效的刷新令牌")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 生成新令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info(f"令牌刷新成功: {user.username}")

    return success_response(
        data={
            "user_id": user.id,
            "token": access_token,
            "refresh_token": new_refresh_token
        },
        message="刷新成功"
    )
