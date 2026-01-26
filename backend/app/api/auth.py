"""
认证相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录

    - **phone**: 手机号
    - **password**: 密码
    """
    # 查找用户
    user = db.query(User).filter(User.phone == user_data.phone).first()
    if not user:
        logger.warning(f"登录失败: 用户不存在 - {user_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误"
        )

    # 验证密码
    if not verify_password(user_data.password, user.password_hash):
        logger.warning(f"登录失败: 密码错误 - {user_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误"
        )

    # 检查用户是否激活
    if not user.is_active:
        logger.warning(f"登录失败: 用户未激活 - {user_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 生成令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info(f"用户登录成功: {user.phone}")

    return Token(
        user_id=user.id,
        token=access_token,
        refresh_token=refresh_token
    )


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **phone**: 手机号
    - **password**: 密码
    - **nickname**: 昵称（可选）
    """
    # 检查手机号是否已注册
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        logger.warning(f"注册失败: 手机号已存在 - {user_data.phone}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册"
        )

    # 创建新用户
    new_user = User(
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        nickname=user_data.nickname or f"用户{user_data.phone[-4:]}"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 生成令牌
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    logger.info(f"新用户注册成功: {new_user.phone}")

    return Token(
        user_id=new_user.id,
        token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
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

    logger.info(f"令牌刷新成功: {user.phone}")

    return Token(
        user_id=user.id,
        token=access_token,
        refresh_token=new_refresh_token
    )
