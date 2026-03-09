"""
规划模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Plan(Base):
    """规划模型"""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True, comment="目标ID")
    content = Column(Text, nullable=False, comment="规划内容(JSON)")
    status = Column(String(20), default="draft", comment="状态: draft/confirmed")
    total_stages = Column(Integer, default=0, comment="阶段数量")
    total_tasks = Column(Integer, default=0, comment="任务数量")
    estimated_total_hours = Column(Float, default=0, comment="预估总工时")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")

    # 关系
    goal = relationship("Goal", back_populates="plans")
    tasks = relationship("Task", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plan(id={self.id}, goal_id={self.goal_id}, status={self.status})>"
