"""
目标模块测试
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date


class TestGoals:
    """目标测试类"""

    def test_create_goal_success(self, client: TestClient, auth_headers):
        """测试创建目标成功"""
        response = client.post(
            "/api/goals",
            json={
                "title": "学习 Vue.js",
                "description": "掌握 Vue3 基础",
                "deadline": "2025-06-30"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "创建成功"
        assert data["data"]["title"] == "学习 Vue.js"

    def test_create_goal_empty_title(self, client: TestClient, auth_headers):
        """测试创建目标标题为空"""
        response = client.post(
            "/api/goals",
            json={"title": ""},
            headers=auth_headers
        )

        assert response.status_code == 422  # 验证错误

    def test_get_goals_empty(self, client: TestClient, auth_headers):
        """测试获取空目标列表"""
        response = client.get("/api/goals", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []

    def test_get_goals_with_data(self, client: TestClient, auth_headers, test_goal):
        """测试获取目标列表"""
        response = client.get("/api/goals", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == "学习 Python"

    def test_get_goal_by_id_success(self, client: TestClient, auth_headers, test_goal):
        """测试根据 ID 获取目标"""
        response = client.get(f"/api/goals/{test_goal.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == test_goal.id
        assert data["data"]["title"] == "学习 Python"

    def test_get_goal_not_found(self, client: TestClient, auth_headers):
        """测试获取不存在的目标"""
        response = client.get("/api/goals/99999", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 2001  # 目标不存在

    def test_delete_goal_success(self, client: TestClient, auth_headers, test_goal):
        """测试删除目标成功"""
        response = client.delete(f"/api/goals/{test_goal.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "删除成功"

    def test_delete_goal_not_found(self, client: TestClient, auth_headers):
        """测试删除不存在的目标"""
        response = client.delete("/api/goals/99999", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 2001
