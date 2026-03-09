"""
API流程集成测试
测试完整的业务流程
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthFlow:
    """认证流程测试"""

    def test_complete_register_login_flow(self, client: TestClient):
        """测试完整的注册-登录流程"""
        # 1. 注册新用户
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": "flowuser",
                "password": "pass123",
                "email": "flow@example.com"
            }
        )
        assert register_response.status_code == 200
        register_data = register_response.json()
        assert register_data["code"] == 0
        assert "token" in register_data["data"]

        # 2. 使用新用户登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "flowuser",
                "password": "pass123"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["code"] == 0
        assert "token" in login_data["data"]

    def test_login_after_register(self, client: TestClient):
        """测试注册后立即登录"""
        # 注册
        client.post(
            "/api/auth/register",
            json={
                "username": "quickuser",
                "password": "pass123",
                "email": "quick@example.com"
            }
        )

        # 登录
        response = client.post(
            "/api/auth/login",
            json={
                "username": "quickuser",
                "password": "pass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["username"] == "quickuser"


class TestGoalFlow:
    """目标管理流程测试"""

    def test_complete_goal_lifecycle(self, client: TestClient, auth_headers: dict):
        """测试目标的完整生命周期"""
        # 1. 创建目标
        create_response = client.post(
            "/api/goals",
            headers=auth_headers,
            json={
                "title": "学习Python",
                "description": "掌握Python编程"
            }
        )
        assert create_response.status_code == 200
        goal_data = create_response.json()["data"]
        goal_id = goal_data["id"]

        # 2. 获取目标列表
        list_response = client.get("/api/goals", headers=auth_headers)
        assert list_response.status_code == 200
        goals = list_response.json()["data"]
        assert len(goals) > 0

        # 3. 获取目标详情
        detail_response = client.get(f"/api/goals/{goal_id}", headers=auth_headers)
        assert detail_response.status_code == 200
        assert detail_response.json()["data"]["title"] == "学习Python"

        # 4. 删除目标
        delete_response = client.delete(f"/api/goals/{goal_id}", headers=auth_headers)
        print(f"删除响应: {delete_response.json()}")
        assert delete_response.status_code == 200


class TestPlanFlow:
    """规划流程测试"""

    def test_create_plan_with_ai(self, client: TestClient, auth_headers: dict, db):
        """测试使用AI创建规划"""
        # 先创建目标
        from app.models import Goal
        goal = Goal(
            user_id=1,
            title="测试目标",
            description="测试描述",
            status="planning"
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

        # 创建规划 - 按照文档定义的接口
        response = client.post(
            "/api/plans/generate",
            headers=auth_headers,
            json={
                "goal_id": goal.id,
                "available_hours_per_day": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "id" in data["data"] or "plan_id" in data["data"]
