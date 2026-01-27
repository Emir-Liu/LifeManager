"""
认证依赖
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.models.user import User


def get_current_user(
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
        detail=ERROR_MESSAGES.get(ErrorCode.TOKEN_INVALID),
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码 Token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前激活用户

    Args:
        current_user: 当前用户

    Returns:
        当前激活用户

    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user
