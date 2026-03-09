"""
Service层测试
"""
import pytest
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.services.task_service import TaskService
from app.services.plan_service import PlanService
from app.services.goal_service import GoalService

from app.models.goal import Goal
from app.models.plan import Plan
from app.models.task import Task
from app.models.user import User

from app.core.exceptions import ErrorCode, ERROR_MESSAGES


class TestTaskService:
    """任务服务测试"""

    def test_create_task_success(self, db: Session, test_user: User, test_goal: Goal):
        """测试成功创建任务"""
        task = TaskService.create_task(
            db=db,
            goal_id=test_goal.id,
            user_id=test_user.id,
            title="学习Python基础",
            due_date=date.today() + timedelta(days=7),
            description="完成Python基础教程",
            estimated_hours=5
        )

        assert task.id is not None
        assert task.title == "学习Python基础"
        assert task.goal_id == test_goal.id
        assert task.estimated_hours == 5

    def test_create_task_invalid_goal(self, db: Session, test_user: User):
        """测试创建任务时目标不存在"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER]):
            TaskService.create_task(
                db=db,
                goal_id=999,
                user_id=test_user.id,
                title="测试任务",
                due_date=date.today() + timedelta(days=7)
            )

    def test_create_task_not_belong_to_user(self, db: Session, test_goal: Goal):
        """测试创建任务时目标不属于用户"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER]):
            TaskService.create_task(
                db=db,
                goal_id=test_goal.id,
                user_id=999,
                title="测试任务",
                due_date=date.today() + timedelta(days=7)
            )

    def test_create_tasks_from_plan(self, db: Session, test_user: User, test_goal: Goal, test_plan: Plan):
        """测试从规划创建任务"""
        tasks = TaskService.create_tasks_from_plan(db, test_plan, available_hours=2)

        assert len(tasks) > 0
        assert test_plan.total_tasks == len(tasks)
        assert test_plan.status == "draft"

    def test_create_tasks_from_plan_skip_weekend(self, db: Session, test_user: User, test_goal: Goal):
        """测试创建任务时跳过周末"""
        plan_data = {
            "stages": [
                {
                    "name": "阶段一",
                    "tasks": [
                        {"title": "任务1", "description": "描述1", "estimated_hours": 2}
                    ]
                }
            ]
        }

        test_goal.deadline = date.today() + timedelta(days=30)
        db.commit()

        plan = Plan(
            goal_id=test_goal.id,
            content=str(plan_data),
            status="draft"
        )
        db.add(plan)
        db.commit()

        tasks = TaskService.create_tasks_from_plan(db, plan, available_hours=2)

        assert len(tasks) > 0
        for task in tasks:
            assert task.due_date.weekday() < 5

    def test_get_user_tasks(self, db: Session, test_user: User, test_goal: Goal, test_task: Task):
        """测试获取用户任务"""
        tasks = TaskService.get_user_tasks(db, test_user.id)
        assert len(tasks) >= 1
        assert test_task in tasks

    def test_get_user_tasks_filter_by_goal(self, db: Session, test_user: User, test_goal: Goal, test_task: Task):
        """测试按目标筛选任务"""
        tasks = TaskService.get_user_tasks(db, test_user.id, goal_id=test_goal.id)
        assert len(tasks) == 1
        assert tasks[0].goal_id == test_goal.id

    def test_get_user_tasks_filter_by_status(self, db: Session, test_user: User, test_task: Task):
        """测试按完成状态筛选任务"""
        test_task.completed = True
        db.commit()

        tasks = TaskService.get_user_tasks(db, test_user.id, status=True)
        assert len(tasks) == 1
        assert tasks[0].completed is True

    def test_get_today_tasks(self, db: Session, test_user: User, test_task: Task):
        """测试获取今日任务"""
        test_task.due_date = date.today()
        db.commit()

        result = TaskService.get_today_tasks(db, test_user.id)
        assert "total" in result
        assert "completed" in result
        assert "data" in result
        assert result["total"] == 1

    def test_get_task_by_id_success(self, db: Session, test_user: User, test_task: Task):
        """测试根据ID获取任务"""
        task = TaskService.get_task_by_id(db, test_task.id, test_user.id)
        assert task.id == test_task.id
        assert task.title == test_task.title

    def test_get_task_by_id_not_found(self, db: Session, test_user: User):
        """测试获取不存在的任务"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.TASK_NOT_FOUND]):
            TaskService.get_task_by_id(db, 999, test_user.id)

    def test_get_task_by_id_not_belong_to_user(self, db: Session, test_task: Task):
        """测试获取不属于用户的任务"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.TASK_NOT_BELONG_TO_USER]):
            TaskService.get_task_by_id(db, test_task.id, 999)

    def test_complete_task(self, db: Session, test_user: User, test_task: Task):
        """测试完成任务"""
        task = TaskService.complete_task(db, test_task.id, test_user.id)
        assert task.completed is True
        assert task.completed_at is not None

    def test_uncomplete_task(self, db: Session, test_user: User, test_task: Task):
        """测试取消完成"""
        test_task.completed = True
        test_task.completed_at = datetime.now()
        db.commit()

        task = TaskService.uncomplete_task(db, test_task.id, test_user.id)
        assert task.completed is False
        assert task.completed_at is None

    def test_delete_task(self, db: Session, test_user: User, test_task: Task):
        """测试删除任务"""
        task_id = test_task.id
        result = TaskService.delete_task(db, task_id, test_user.id)
        assert result is True

        deleted_task = db.query(Task).filter(Task.id == task_id).first()
        assert deleted_task is None


class TestPlanService:
    """规划服务测试"""

    def test_generate_plan_existing_draft(self, db: Session, test_user: User, test_goal: Goal, test_plan: Plan):
        """测试生成规划时已有草稿"""
        test_plan.status = "draft"
        db.commit()

        plan = PlanService.generate_plan(db, test_user.id, test_goal.id)
        assert plan.id == test_plan.id
        assert plan.status == "draft"

    def test_get_plan_by_id_success(self, db: Session, test_user: User, test_plan: Plan):
        """测试根据ID获取规划"""
        plan = PlanService.get_plan_by_id(db, test_plan.id, test_user.id)
        assert plan.id == test_plan.id

    def test_get_plan_by_id_not_found(self, db: Session, test_user: User):
        """测试获取不存在的规划"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.PLAN_NOT_FOUND]):
            PlanService.get_plan_by_id(db, 999, test_user.id)

    def test_get_plan_by_id_not_belong_to_user(self, db: Session, test_plan: Plan):
        """测试获取不属于用户的规划"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER]):
            PlanService.get_plan_by_id(db, test_plan.id, 999)

    def test_confirm_plan_success(self, db: Session, test_user: User, test_plan: Plan, test_goal: Goal):
        """测试确认规划"""
        result = PlanService.confirm_plan(db, test_plan.id, test_user.id)
        assert "plan_id" in result
        assert "tasks_created" in result
        assert result["plan_id"] == test_plan.id

        db.refresh(test_plan)
        assert test_plan.status == "confirmed"

        db.refresh(test_goal)
        assert test_goal.status == "confirmed"

    def test_confirm_plan_already_confirmed(self, db: Session, test_user: User, test_plan: Plan):
        """测试确认已确认的规划"""
        test_plan.status = "confirmed"
        db.commit()

        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY]):
            PlanService.confirm_plan(db, test_plan.id, test_user.id)

    def test_update_plan_success(self, db: Session, test_user: User, test_plan: Plan):
        """测试更新规划"""
        new_content = {
            "stages": [
                {
                    "name": "更新后的阶段",
                    "tasks": [
                        {"title": "新任务", "description": "新描述", "estimated_hours": 3}
                    ]
                }
            ]
        }

        plan = PlanService.update_plan(db, test_plan.id, test_user.id, new_content)
        assert plan.total_stages == 1
        assert plan.total_tasks == 1
        assert plan.estimated_total_hours == 3

    def test_update_plan_confirmed_plan(self, db: Session, test_user: User, test_plan: Plan):
        """测试更新已确认的规划"""
        test_plan.status = "confirmed"
        db.commit()

        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY]):
            PlanService.update_plan(db, test_plan.id, test_user.id, {})

    def test_delete_plan_success(self, db: Session, test_user: User, test_plan: Plan):
        """测试删除规划"""
        plan_id = test_plan.id
        result = PlanService.delete_plan(db, plan_id, test_user.id)
        assert result is True

        deleted_plan = db.query(Plan).filter(Plan.id == plan_id).first()
        assert deleted_plan is None

    def test_delete_plan_confirmed(self, db: Session, test_user: User, test_plan: Plan):
        """测试删除已确认的规划"""
        test_plan.status = "confirmed"
        db.commit()

        with pytest.raises(ValueError, match="已确认的规划不能删除"):
            PlanService.delete_plan(db, test_plan.id, test_user.id)

    def test_get_user_plans(self, db: Session, test_user: User, test_plan: Plan):
        """测试获取用户规划"""
        plans = PlanService.get_user_plans(db, test_user.id)
        assert len(plans) >= 1
        assert test_plan in plans

    def test_get_user_plans_filter_by_goal(self, db: Session, test_user: User, test_plan: Plan, test_goal: Goal):
        """测试按目标筛选规划"""
        plans = PlanService.get_user_plans(db, test_user.id, goal_id=test_goal.id)
        assert len(plans) == 1
        assert plans[0].goal_id == test_goal.id


class TestGoalService:
    """目标服务测试"""

    def test_create_goal_success(self, db: Session, test_user: User):
        """测试成功创建目标"""
        goal = GoalService.create_goal(
            db=db,
            user_id=test_user.id,
            title="学习AI",
            description="掌握机器学习基础"
        )

        assert goal.id is not None
        assert goal.title == "学习AI"
        assert goal.user_id == test_user.id
        assert goal.status == "planning"

    def test_create_goal_empty_title(self, db: Session, test_user: User):
        """测试创建空标题目标"""
        with pytest.raises(ValueError, match="目标标题不能为空"):
            GoalService.create_goal(db, test_user.id, "")

    def test_get_user_goals(self, db: Session, test_user: User, test_goal: Goal):
        """测试获取用户目标"""
        goals = GoalService.get_user_goals(db, test_user.id)
        assert len(goals) >= 1
        assert test_goal in goals

    def test_get_user_goals_filter_by_status(self, db: Session, test_user: User, test_goal: Goal):
        """测试按状态筛选目标"""
        goals = GoalService.get_user_goals(db, test_user.id, status="planning")
        assert len(goals) >= 1
        for goal in goals:
            assert goal.status == "planning"

    def test_get_goal_by_id_success(self, db: Session, test_user: User, test_goal: Goal):
        """测试根据ID获取目标"""
        goal = GoalService.get_goal_by_id(db, test_goal.id, test_user.id)
        assert goal.id == test_goal.id

    def test_get_goal_by_id_not_found(self, db: Session, test_user: User):
        """测试获取不存在的目标"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.GOAL_NOT_FOUND]):
            GoalService.get_goal_by_id(db, 999, test_user.id)

    def test_get_goal_by_id_not_belong_to_user(self, db: Session, test_goal: Goal):
        """测试获取不属于用户的目标"""
        with pytest.raises(ValueError, match=ERROR_MESSAGES[ErrorCode.GOAL_NOT_BELONG_TO_USER]):
            GoalService.get_goal_by_id(db, test_goal.id, 999)

    def test_get_goal_detail(self, db: Session, test_user: User, test_goal: Goal, test_task: Task):
        """测试获取目标详情"""
        detail = GoalService.get_goal_detail(db, test_goal.id, test_user.id)
        assert detail["id"] == test_goal.id
        assert detail["title"] == test_goal.title
        assert "tasks_count" in detail
        assert "completed_tasks" in detail

    def test_update_goal_success(self, db: Session, test_user: User, test_goal: Goal):
        """测试更新目标"""
        goal = GoalService.update_goal(
            db,
            test_goal.id,
            test_user.id,
            title="更新后的标题",
            description="更新后的描述"
        )
        assert goal.title == "更新后的标题"
        assert goal.description == "更新后的描述"

    def test_delete_goal_success(self, db: Session, test_user: User, test_goal: Goal):
        """测试删除目标"""
        goal_id = test_goal.id
        result = GoalService.delete_goal(db, goal_id, test_user.id)
        assert result is True

        deleted_goal = db.query(Goal).filter(Goal.id == goal_id).first()
        assert deleted_goal is None

    def test_update_goal_status_success(self, db: Session, test_user: User, test_goal: Goal):
        """测试更新目标状态"""
        goal = GoalService.update_goal_status(db, test_goal.id, test_user.id, "confirmed")
        assert goal.status == "confirmed"

    def test_update_goal_status_invalid(self, db: Session, test_user: User, test_goal: Goal):
        """测试更新为无效状态"""
        with pytest.raises(ValueError, match="无效的状态值"):
            GoalService.update_goal_status(db, test_goal.id, test_user.id, "invalid")

    def test_get_goal_statistics(self, db: Session, test_user: User, test_goal: Goal):
        """测试获取目标统计"""
        stats = GoalService.get_goal_statistics(db, test_user.id)
        assert "total" in stats
        assert "inProgress" in stats
        assert "completed" in stats
        assert stats["total"] >= 1
