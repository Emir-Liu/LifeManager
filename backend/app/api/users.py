"""
用户管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


# 依赖注入：获取当前用户
def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    """获取当前登录用户"""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="无效的令牌")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息

    需要有效的访问令牌
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息

    需要有效的访问令牌
    """
    if user_data.nickname is not None:
        current_user.nickname = user_data.nickname
    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url

    db.commit()
    db.refresh(current_user)

    return current_user
