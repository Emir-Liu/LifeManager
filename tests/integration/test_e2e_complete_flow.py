"""
E2E完整流程测试
端到端测试用户从注册到任务完成的完整流程
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date

import sys
sys.path.insert(0, '../backend')
from main import app
from app.core.database import get_db


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """数据库会话"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


class TestE2ECompleteFlow:
    """完整E2E流程测试"""

    def test_complete_user_flow(self, client: TestClient):
        """测试完整用户流程：注册→登录→创建目标→AI规划→确认规划→完成任务"""

        # ========== 步骤1: 用户注册 ==========
        register_data = {
            "username": "e2e_test_user",
            "password": "Test123456",
            "email": "e2e_test@example.com"
        }

        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 200
        register_result = response.json()
        assert register_result["code"] == 0
        print("[E2E] 步骤1: 用户注册成功")

        # ========== 步骤2: 用户登录 ==========
        login_data = {
            "username": "e2e_test_user",
            "password": "Test123456"
        }

        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        login_result = response.json()
        assert login_result["code"] == 0
        assert "access_token" in login_result["data"]
        token = login_result["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[E2E] 步骤2: 用户登录成功")

        # ========== 步骤3: 创建目标 ==========
        goal_data = {
            "title": "学习Python编程",
            "description": "在3个月内掌握Python基础和进阶知识",
            "deadline": "2026-06-30"
        }

        response = client.post("/api/goals", json=goal_data, headers=headers)
        assert response.status_code == 200
        create_goal_result = response.json()
        assert create_goal_result["code"] == 0
        goal_id = create_goal_result["data"]["id"]
        print("[E2E] 步骤3: 创建目标成功")

        # ========== 步骤4: 生成AI规划 ==========
        plan_data = {
            "goal_id": goal_id,
            "available_hours": 2
        }

        response = client.post("/api/plans", json=plan_data, headers=headers)
        assert response.status_code == 200
        generate_plan_result = response.json()
        assert generate_plan_result["code"] == 0
        plan_id = generate_plan_result["data"]["id"]
        print("[E2E] 步骤4: AI规划生成成功")

        # ========== 步骤5: 确认规划 ==========
        response = client.post(f"/api/plans/{plan_id}/confirm", headers=headers)
        assert response.status_code == 200
        confirm_result = response.json()
        assert confirm_result["code"] == 0
        print("[E2E] 步骤5: 规划确认成功")

        # ========== 步骤6: 获取任务列表 ==========
        response = client.get("/api/tasks", headers=headers)
        assert response.status_code == 200
        tasks_result = response.json()
        assert tasks_result["code"] == 0
        tasks = tasks_result["data"]
        assert len(tasks) > 0
        task_id = tasks[0]["id"]
        print(f"[E2E] 步骤6: 获取任务列表成功，共{len(tasks)}个任务")

        # ========== 步骤7: 查看任务详情 ==========
        response = client.get(f"/api/tasks/{task_id}", headers=headers)
        assert response.status_code == 200
        task_detail_result = response.json()
        assert task_detail_result["code"] == 0
        assert task_detail_result["data"]["id"] == task_id
        print("[E2E] 步骤7: 查看任务详情成功")

        # ========== 步骤8: 完成任务 ==========
        response = client.put(f"/api/tasks/{task_id}/complete", headers=headers)
        assert response.status_code == 200
        complete_result = response.json()
        assert complete_result["code"] == 0
        print("[E2E] 步骤8: 任务完成成功")

        # ========== 步骤9: 验证目标进度 ==========
        response = client.get("/api/goals/statistics", headers=headers)
        assert response.status_code == 200
        stats_result = response.json()
        assert stats_result["code"] == 0
        assert stats_result["data"]["total"] >= 1
        print("[E2E] 步骤9: 查看目标统计成功")

        # ========== 步骤10: 删除目标 ==========
        response = client.delete(f"/api/goals/{goal_id}", headers=headers)
        assert response.status_code == 200
        delete_result = response.json()
        assert delete_result["code"] == 0
        print("[E2E] 步骤10: 删除目标成功")

        print("\n[E2E] ========== 完整流程测试通过 ==========")


class TestE2EExceptionScenarios:
    """E2E异常场景测试"""

    def test_login_with_wrong_password(self, client: TestClient):
        """测试错误密码登录"""
        response = client.post("/api/auth/login", data={
            "username": "e2e_test_user",
            "password": "wrong_password"
        })
        assert response.status_code == 401
        print("[E2E-Exception] 错误密码登录测试通过")

    def test_access_without_token(self, client: TestClient):
        """测试未认证访问"""
        response = client.get("/api/goals")
        assert response.status_code == 401
        print("[E2E-Exception] 未认证访问测试通过")

    def test_create_goal_with_empty_title(self, client: TestClient):
        """测试创建空标题目标"""
        # 先注册并登录
        client.post("/api/auth/register", json={
            "username": "test_empty_title",
            "password": "Test123456"
        })
        login_response = client.post("/api/auth/login", data={
            "username": "test_empty_title",
            "password": "Test123456"
        })
        token = login_response.json()["data"]["access_token"]

        # 创建空标题目标
        response = client.post("/api/goals", json={
            "title": "",
            "description": "测试"
        }, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["code"] == 1010  # GOAL_TITLE_EMPTY
        print("[E2E-Exception] 空标题目标测试通过")

    def test_delete_goal_with_tasks(self, client: TestClient, db_session):
        """测试删除包含任务的目标"""
        # 注册、登录、创建目标
        from app.models.user import User
        from app.models.goal import Goal
        from app.models.task import Task

        user = User(username="test_delete_with_tasks", password_hash="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        goal = Goal(user_id=user.id, title="测试", status="confirmed")
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        task = Task(goal_id=goal.id, title="任务", due_date=date.today())
        db_session.add(task)
        db_session.commit()

        # 登录
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        # 删除目标
        response = client.delete(f"/api/goals/{goal.id}", headers=headers)
        assert response.status_code == 200

        # 验证任务也被级联删除
        deleted_task = db_session.query(Task).filter(Task.id == task.id).first()
        assert deleted_task is None
        print("[E2E-Exception] 级联删除测试通过")

    def test_ai_api_failure_fallback(self, client: TestClient, db_session):
        """测试AI API失败时的降级方案"""
        # 注册、登录、创建目标
        from app.models.user import User
        from app.models.goal import Goal
        from app.core.security import create_access_token

        user = User(username="test_ai_fallback", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        goal = Goal(user_id=user.id, title="测试", status="confirmed")
        db_session.add(goal)
        db_session.commit()

        token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {token}"}

        # 不配置API Key，使用降级方案
        response = client.post("/api/plans", json={
            "goal_id": goal.id,
            "available_hours": 2
        }, headers=headers)

        # 即使没有AI API也应该返回降级方案
        assert response.status_code == 200
        print("[E2E-Exception] AI降级方案测试通过")


class TestE2EBoundaryConditions:
    """E2E边界条件测试"""

    def test_create_multiple_goals(self, client: TestClient):
        """测试创建多个目标"""
        # 注册登录
        client.post("/api/auth/register", json={
            "username": "test_multi_goals",
            "password": "Test123456"
        })
        login_response = client.post("/api/auth/login", data={
            "username": "test_multi_goals",
            "password": "Test123456"
        })
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 创建多个目标
        for i in range(5):
            response = client.post("/api/goals", json={
                "title": f"目标{i}",
                "description": f"描述{i}"
            }, headers=headers)
            assert response.status_code == 200

        # 获取所有目标
        response = client.get("/api/goals", headers=headers)
        assert response.status_code == 200
        assert len(response.json()["data"]) >= 5
        print("[E2E-Boundary] 多目标创建测试通过")

    def test_complete_all_tasks(self, client: TestClient):
        """测试完成所有任务"""
        # 注册、登录、创建目标、生成规划
        username = "test_complete_all"
        client.post("/api/auth/register", json={
            "username": username,
            "password": "Test123456"
        })
        login_response = client.post("/api/auth/login", data={
            "username": username,
            "password": "Test123456"
        })
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 创建目标
        goal_response = client.post("/api/goals", json={
            "title": "测试目标",
            "description": "描述"
        }, headers=headers)
        goal_id = goal_response.json()["data"]["id"]

        # 生成规划
        plan_response = client.post("/api/plans", json={
            "goal_id": goal_id
        }, headers=headers)
        plan_id = plan_response.json()["data"]["id"]

        # 确认规划
        client.post(f"/api/plans/{plan_id}/confirm", headers=headers)

        # 获取所有任务
        tasks_response = client.get("/api/tasks", headers=headers)
        tasks = tasks_response.json()["data"]

        # 完成所有任务
        for task in tasks:
            response = client.put(f"/api/tasks/{task['id']}/complete", headers=headers)
            assert response.status_code == 200

        print("[E2E-Boundary] 完成所有任务测试通过")
