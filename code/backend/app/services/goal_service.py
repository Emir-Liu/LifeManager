"""
目标服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.goal import Goal
from app.models.task import Task
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.core.logger import logger


class GoalService:
    """目标业务逻辑服务"""

    @staticmethod
    def create_goal(db: Session, user_id: int, title: str, description: str = None, deadline=None) -> Goal:
        """
        创建目标

        Args:
            db: 数据库会话
            user_id: 用户 ID
            title: 目标标题
            description: 目标描述
            deadline: 截止日期

        Returns:
            创建的目标对象

        Raises:
            ValueError: 参数错误
        """
        if not title or not title.strip():
            raise ValueError("目标标题不能为空")

        goal = Goal(
            user_id=user_id,
            title=title.strip(),
            description=description,
            deadline=deadline,
            status="planning"
        )
        db.add(goal)
        # 注意：commit 由 API 层控制

        logger.info(f"创建目标成功: {goal.id}, 用户: {user_id}")
        return goal

    @staticmethod
    def get_user_goals(db: Session, user_id: int, status: Optional[str] = None) -> List[Goal]:
        """
        获取用户的目标列表

        Args:
            db: 数据库会话
            user_id: 用户 ID
            status: 状态筛选（可选）

        Returns:
            目标列表
        """
        query = db.query(Goal).filter(Goal.user_id == user_id)

        if status:
            query = query.filter(Goal.status == status)

        goals = query.order_by(Goal.created_at.desc()).all()
        return goals

    @staticmethod
    def get_goal_by_id(db: Session, goal_id: int, user_id: int) -> Optional[Goal]:
        """
        根据 ID 获取目标（验证所属用户）

        Args:
            db: 数据库会话
            goal_id: 目标 ID
            user_id: 用户 ID

        Returns:
            目标对象或 None

        Raises:
            ValueError: 目标不存在或不属于当前用户
        """
        goal = db.query(Goal).filter(Goal.id == goal_id).first()

        if not goal:
            raise ValueError(ERROR_MESSAGES[ErrorCode.GOAL_NOT_FOUND])

        if goal.user_id != user_id:
            raise ValueError(ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER])

        return goal

    @staticmethod
    def get_goal_detail(db: Session, goal_id: int, user_id: int) -> dict:
        """
        获取目标详情（包含统计信息）

        Args:
            db: 数据库会话
            goal_id: 目标 ID
            user_id: 用户 ID

        Returns:
            目标详情字典
        """
        goal = GoalService.get_goal_by_id(db, goal_id, user_id)

        # 获取统计信息
        tasks_count = db.query(Task).filter(Task.goal_id == goal_id).count()
        completed_tasks = db.query(Task).filter(
            Task.goal_id == goal_id,
            Task.completed == True
        ).count()

        return {
            **goal.__dict__,
            "tasks_count": tasks_count,
            "completed_tasks": completed_tasks
        }

    @staticmethod
    def update_goal(db: Session, goal_id: int, user_id: int, **kwargs) -> Goal:
        """
        更新目标

        Args:
            db: 数据库会话
            goal_id: 目标 ID
            user_id: 用户 ID
            **kwargs: 更新字段

        Returns:
            更新后的目标对象
        """
        goal = GoalService.get_goal_by_id(db, goal_id, user_id)

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(goal, key) and value is not None:
                setattr(goal, key, value)

        db.commit()
        db.refresh(goal)

        logger.info(f"更新目标成功: {goal_id}")
        return goal

    @staticmethod
    def delete_goal(db: Session, goal_id: int, user_id: int) -> bool:
        """
        删除目标

        Args:
            db: 数据库会话
            goal_id: 目标 ID
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        goal = GoalService.get_goal_by_id(db, goal_id, user_id)

        db.delete(goal)
        # 注意：commit 由 API 层控制

        logger.info(f"删除目标成功: {goal_id}")
        return True

    @staticmethod
    def update_goal_status(db: Session, goal_id: int, user_id: int, status: str) -> Goal:
        """
        更新目标状态

        Args:
            db: 数据库会话
            goal_id: 目标 ID
            user_id: 用户 ID
            status: 新状态

        Returns:
            更新后的目标对象
        """
        if status not in ["planning", "confirmed", "completed"]:
            raise ValueError("无效的状态值")

        return GoalService.update_goal(db, goal_id, user_id, status=status)

    @staticmethod
    def get_goal_statistics(db: Session, user_id: int) -> dict:
        """
        获取目标统计信息

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            统计数据字典
        """
        total = db.query(Goal).filter(Goal.user_id == user_id).count()
        in_progress = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status.in_(["planning", "confirmed"])
        ).count()
        completed = db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "completed"
        ).count()

        return {
            "total": total,
            "inProgress": in_progress,
            "completed": completed
        }


# 全局实例
goal_service = GoalService()
