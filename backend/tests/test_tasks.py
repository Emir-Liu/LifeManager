"""
任务模块测试
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date


class TestTasks:
    """任务测试类"""

    def test_get_tasks_empty(self, client: TestClient, auth_headers):
        """测试获取空任务列表"""
        response = client.get("/api/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []

    def test_get_tasks_with_data(self, client: TestClient, auth_headers, test_task):
        """测试获取任务列表"""
        response = client.get("/api/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 1

    def test_get_today_tasks(self, client: TestClient, auth_headers, test_task):
        """测试获取今日任务"""
        response = client.get("/api/tasks/today", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total" in data["data"]
        assert "completed" in data["data"]

    def test_create_task_success(self, client: TestClient, auth_headers, test_goal):
        """测试创建任务成功"""
        response = client.post(
            "/api/tasks",
            json={
                "goal_id": test_goal.id,
                "title": "新任务",
                "due_date": str(date.today()),
                "estimated_hours": 2
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "创建成功"
        assert data["data"]["title"] == "新任务"

    def test_complete_task_success(self, client: TestClient, auth_headers, test_task):
        """测试完成任务成功"""
        response = client.put(f"/api/tasks/{test_task.id}/complete", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "任务已完成"
        assert data["data"]["completed"] == True

    def test_uncomplete_task_success(self, client: TestClient, auth_headers, test_task):
        """测试取消完成任务成功"""
        # 先完成任务
        client.put(f"/api/tasks/{test_task.id}/complete", headers=auth_headers)

        # 取消完成
        response = client.put(f"/api/tasks/{test_task.id}/uncomplete", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "已取消完成状态"
        assert data["data"]["completed"] == False

    def test_delete_task_success(self, client: TestClient, auth_headers, test_task):
        """测试删除任务成功"""
        response = client.delete(f"/api/tasks/{test_task.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "删除成功"
