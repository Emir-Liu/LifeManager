"""
任务模型
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True, comment="目标ID")
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=True, comment="规划ID")
    title = Column(String(200), nullable=False, comment="任务标题")
    description = Column(Text, nullable=True, comment="任务描述")
    due_date = Column(Date, nullable=False, index=True, comment="截止日期")
    completed = Column(Boolean, default=False, comment="是否完成")
    stage_name = Column(String(100), nullable=True, comment="阶段名称")
    estimated_hours = Column(Integer, default=0, comment="预估工时")
    task_order = Column(Integer, default=0, comment="任务顺序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关系
    goal = relationship("Goal", back_populates="tasks")
    plan = relationship("Plan", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, completed={self.completed})>"
