"""
规划服务
"""
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.plan import Plan
from app.models.goal import Goal
from app.models.user import User
from app.services.task_service import task_service
from app.services.ai_service import ai_service
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.core.logger import logger


class PlanService:
    """规划业务逻辑服务"""

    @staticmethod
    def generate_plan(
        db: Session,
        user_id: int,
        goal_id: int,
        available_hours_per_day: float = 2.0
    ) -> Plan:
        """
        生成规划（调用 AI）

        Args:
            db: 数据库会话
            user_id: 用户 ID
            goal_id: 目标 ID
            available_hours_per_day: 每天可用小时数

        Returns:
            生成的规划对象
        """
        # 获取目标信息
        goal = db.query(Goal).filter(Goal.id == goal_id).first()

        if not goal:
            raise ValueError(ERROR_MESSAGES[ErrorCode.GOAL_NOT_FOUND])

        if goal.user_id != user_id:
            raise ValueError(ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER])

        # 检查是否已有草稿规划
        existing_plan = db.query(Plan).filter(
            Plan.goal_id == goal_id,
            Plan.status == "draft"
        ).first()

        if existing_plan:
            logger.info(f"目标 {goal_id} 已存在草稿规划")
            return existing_plan

        try:
            # 调用 AI 生成规划
            logger.info(f"开始为目标 {goal_id} 生成规划")

            plan_data = ai_service.generate_plan(
                goal_title=goal.title,
                goal_description=goal.description or "",
                deadline=str(goal.deadline) if goal.deadline else "",
                available_hours=int(available_hours_per_day)
            )

            # 保存规划
            plan = Plan(
                goal_id=goal_id,
                content=json.dumps(plan_data, ensure_ascii=False),
                status="draft",
                total_stages=len(plan_data.get("stages", [])),
                total_tasks=sum(
                    len(stage.get("tasks", []))
                    for stage in plan_data.get("stages", [])
                ),
                estimated_total_hours=sum(
                    task.get("estimated_hours", 0)
                    for stage in plan_data.get("stages", [])
                    for task in stage.get("tasks", [])
                )
            )

            db.add(plan)
            db.commit()
            db.refresh(plan)

            logger.info(f"规划生成成功: {plan.id}")
            return plan

        except Exception as e:
            db.rollback()
            logger.error(f"生成规划失败: {e}")
            raise

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: int, user_id: int) -> Optional[Plan]:
        """
        根据 ID 获取规划（验证所属用户）

        Args:
            db: 数据库会话
            plan_id: 规划 ID
            user_id: 用户 ID

        Returns:
            规划对象或 None

        Raises:
            ValueError: 规划不存在或不属于当前用户
        """
        plan = db.query(Plan).join(Goal).filter(Plan.id == plan_id).first()

        if not plan:
            raise ValueError(ERROR_MESSAGES[ErrorCode.PLAN_NOT_FOUND])

        if plan.goal.user_id != user_id:
            raise ValueError(ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER])

        return plan

    @staticmethod
    def confirm_plan(db: Session, plan_id: int, user_id: int, content: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        确认规划（创建所有任务）

        Args:
            db: 数据库会话
            plan_id: 规划 ID
            user_id: 用户 ID
            content: 修改后的规划内容（可选）

        Returns:
            包含规划 ID 和任务数量的字典
        """
        plan = PlanService.get_plan_by_id(db, plan_id, user_id)

        if plan.status == "confirmed":
            raise ValueError(ERROR_MESSAGES[ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY])

        # 如果提供了修改后的内容，更新规划
        if content:
            plan.content = json.dumps(content, ensure_ascii=False)
            # 更新统计信息
            stages = content.get("stages", [])
            plan.total_stages = len(stages)
            plan.total_tasks = sum(len(s.get("tasks", [])) for s in stages)
            plan.estimated_total_hours = sum(
                t.get("estimated_hours", 0)
                for s in stages
                for t in s.get("tasks", [])
            )
            db.commit()

        # 创建任务
        tasks = task_service.create_tasks_from_plan(db, plan)

        # 更新规划状态
        plan.status = "confirmed"

        # 更新目标状态
        plan.goal.status = "confirmed"

        db.commit()

        logger.info(f"规划 {plan_id} 确认成功，创建 {len(tasks)} 个任务")

        return {
            "plan_id": plan.id,
            "tasks_created": len(tasks)
        }

    @staticmethod
    def update_plan(db: Session, plan_id: int, user_id: int, content: Dict[str, Any]) -> Plan:
        """
        更新规划

        Args:
            db: 数据库会话
            plan_id: 规划 ID
            user_id: 用户 ID
            content: 更新的规划内容

        Returns:
            更新后的规划对象
        """
        plan = PlanService.get_plan_by_id(db, plan_id, user_id)

        if plan.status == "confirmed":
            raise ValueError(ERROR_MESSAGES[ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY])

        # 更新规划内容
        plan.content = json.dumps(content, ensure_ascii=False)

        # 更新统计信息
        stages = content.get("stages", [])
        plan.total_stages = len(stages)
        plan.total_tasks = sum(len(s.get("tasks", [])) for s in stages)
        plan.estimated_total_hours = sum(
            t.get("estimated_hours", 0)
            for s in stages
            for t in s.get("tasks", [])
        )

        db.commit()
        db.refresh(plan)

        logger.info(f"更新规划成功: {plan_id}")
        return plan

    @staticmethod
    def delete_plan(db: Session, plan_id: int, user_id: int) -> bool:
        """
        删除规划

        Args:
            db: 数据库会话
            plan_id: 规划 ID
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        plan = PlanService.get_plan_by_id(db, plan_id, user_id)

        if plan.status == "confirmed":
            raise ValueError("已确认的规划不能删除")

        db.delete(plan)
        db.commit()

        logger.info(f"删除规划成功: {plan_id}")
        return True

    @staticmethod
    def get_user_plans(db: Session, user_id: int, goal_id: Optional[int] = None) -> list:
        """
        获取用户的规划列表

        Args:
            db: 数据库会话
            user_id: 用户 ID
            goal_id: 目标 ID（可选）

        Returns:
            规划列表
        """
        query = db.query(Plan).join(Goal).filter(Goal.user_id == user_id)

        if goal_id:
            query = query.filter(Plan.goal_id == goal_id)

        plans = query.order_by(Plan.created_at.desc()).all()
        return plans


# 全局实例
plan_service = PlanService()
