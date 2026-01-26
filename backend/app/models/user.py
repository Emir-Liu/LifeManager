"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func
from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(100), nullable=True, comment="昵称")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")
    fcm_token = Column(String(255), nullable=True, comment="FCM推送Token")
    is_active = Column(Boolean, default=True, comment="是否激活")
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone}, nickname={self.nickname})>"
