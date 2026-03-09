"""
任务服务
"""
import json
import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.task import Task
from app.models.goal import Goal
from app.models.plan import Plan
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.core.logger import logger


class TaskService:
    """任务业务逻辑服务"""

    @staticmethod
    def create_task(
        db: Session,
        goal_id: int,
        user_id: int,
        title: str,
        due_date,
        description: str = None,
        plan_id: int = None,
        estimated_hours: int = 0
    ) -> Task:
        """
        创建任务

        Args:
            db: 数据库会话
            goal_id: 目标 ID
            user_id: 用户 ID
            title: 任务标题
            due_date: 截止日期
            description: 任务描述
            plan_id: 规划 ID
            estimated_hours: 预估工时

        Returns:
            创建的任务对象
        """
        # 验证目标是否属于当前用户
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal or goal.user_id != user_id:
            raise ValueError(ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER])

        task = Task(
            goal_id=goal_id,
            plan_id=plan_id,
            title=title,
            description=description,
            due_date=due_date,
            estimated_hours=estimated_hours
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"创建任务成功: {task.id}")
        return task

    @staticmethod
    def create_tasks_from_plan(db: Session, plan: Plan, available_hours: int = 2) -> List[Task]:
        """
        根据规划创建任务

        Args:
            db: 数据库会话
            plan: 规划对象
            available_hours: 每天可用小时数

        Returns:
            创建的任务列表
        """
        try:
            # 解析规划内容
            plan_data = json.loads(plan.content)
            stages = plan_data.get("stages", [])

            # 获取目标信息
            goal = plan.goal
            deadline = goal.deadline
            start_date = datetime.date.today()

            # 计算可用天数
            if deadline:
                delta = deadline - start_date
                available_days = delta.days
                if available_days <= 0:
                    available_days = 1
            else:
                available_days = 30  # 默认30天

            # 按日期分配任务
            tasks = []
            current_date = start_date
            task_order = 0

            for stage in stages:
                stage_name = stage.get("name", "")
                for task_data in stage.get("tasks", []):
                    # 跳过周末
                    while current_date.weekday() >= 5:
                        current_date += datetime.timedelta(days=1)

                    # 创建任务
                    task = Task(
                        goal_id=plan.goal_id,
                        plan_id=plan.id,
                        title=task_data.get("title"),
                        description=task_data.get("description"),
                        estimated_hours=int(task_data.get("estimated_hours", 0)),
                        due_date=current_date,
                        stage_name=stage_name,
                        task_order=task_order
                    )
                    db.add(task)
                    tasks.append(task)

                    # 移动到下一天
                    current_date += datetime.timedelta(days=1)
                    task_order += 1

            # 提交到数据库
            db.commit()

            # 更新规划统计信息
            plan.total_stages = len(stages)
            plan.total_tasks = len(tasks)
            plan.estimated_total_hours = sum(
                task.get("estimated_hours", 0)
                for stage in stages
                for task in stage.get("tasks", [])
            )
            db.commit()

            logger.info(f"根据规划创建 {len(tasks)} 个任务成功")
            return tasks

        except Exception as e:
            db.rollback()
            logger.error(f"创建任务失败: {e}")
            raise

    @staticmethod
    def get_user_tasks(
        db: Session,
        user_id: int,
        goal_id: Optional[int] = None,
        date: Optional[datetime.date] = None,
        status: Optional[bool] = None
    ) -> List[Task]:
        """
        获取用户的任务列表

        Args:
            db: 数据库会话
            user_id: 用户 ID
            goal_id: 目标 ID（可选）
            date: 日期（可选）
            status: 完成状态（可选）

        Returns:
            任务列表
        """
        # 关联查询目标验证用户
        from sqlalchemy.orm import joinedload
        query = db.query(Task).join(Goal).filter(Goal.user_id == user_id)

        if goal_id:
            query = query.filter(Task.goal_id == goal_id)

        if date:
            query = query.filter(Task.due_date == date)
            logger.debug(f"筛选日期: {date}")

        if status is not None:
            query = query.filter(Task.completed == status)

        tasks = query.order_by(Task.task_order.asc()).all()
        logger.info(f"查询到 {len(tasks)} 个任务")
        return tasks

    @staticmethod
    def get_today_tasks(db: Session, user_id: int) -> dict:
        """
        获取今日任务

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            包含任务列表和统计信息的字典
        """
        today = datetime.date.today()
        
        logger.info(f"获取用户 {user_id} 今天的任务，日期: {today}")

        tasks = TaskService.get_user_tasks(db, user_id, date=today)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.completed)
        
        logger.info(f"找到 {total} 个任务，已完成 {completed} 个")

        return {
            "total": total,
            "completed": completed,
            "data": tasks
        }

    @staticmethod
    def get_task_by_id(db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """
        根据 ID 获取任务（验证所属用户）

        Args:
            db: 数据库会话
            task_id: 任务 ID
            user_id: 用户 ID

        Returns:
            任务对象或 None

        Raises:
            ValueError: 任务不存在或不属于当前用户
        """
        task = db.query(Task).join(Goal).filter(Task.id == task_id).first()

        if not task:
            raise ValueError(ERROR_MESSAGES[ErrorCode.TASK_NOT_FOUND])

        if task.goal.user_id != user_id:
            raise ValueError(ERROR_MESSAGES[ErrorCode.TASK_NOT_BELONG_TO_USER])

        return task

    @staticmethod
    def complete_task(db: Session, task_id: int, user_id: int) -> Task:
        """
        完成任务

        Args:
            db: 数据库会话
            task_id: 任务 ID
            user_id: 用户 ID

        Returns:
            更新后的任务对象
        """
        task = TaskService.get_task_by_id(db, task_id, user_id)

        task.completed = True
        task.completed_at = datetime.datetime.now()

        db.commit()
        db.refresh(task)

        logger.info(f"完成任务: {task_id}")
        return task

    @staticmethod
    def uncomplete_task(db: Session, task_id: int, user_id: int) -> Task:
        """
        取消完成任务

        Args:
            db: 数据库会话
            task_id: 任务 ID
            user_id: 用户 ID

        Returns:
            更新后的任务对象
        """
        task = TaskService.get_task_by_id(db, task_id, user_id)

        task.completed = False
        task.completed_at = None

        db.commit()
        db.refresh(task)

        logger.info(f"取消完成任务: {task_id}")
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> bool:
        """
        删除任务

        Args:
            db: 数据库会话
            task_id: 任务 ID
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        task = TaskService.get_task_by_id(db, task_id, user_id)

        db.delete(task)
        db.commit()

        logger.info(f"删除任务: {task_id}")
        return True


# 全局实例
task_service = TaskService()
