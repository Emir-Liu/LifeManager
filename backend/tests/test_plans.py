"""
规划模块测试
"""
import pytest
from fastapi.testclient import TestClient


class TestPlans:
    """规划测试类"""

    def test_generate_plan_success(self, client: TestClient, auth_headers, test_goal):
        """测试生成规划成功"""
        response = client.post(
            "/api/plans/generate",
            json={
                "goal_id": test_goal.id,
                "available_hours_per_day": 2
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "规划生成成功"
        assert "plan_id" in data["data"]
        assert "content" in data["data"]

    def test_generate_plan_goal_not_found(self, client: TestClient, auth_headers):
        """测试生成规划目标不存在"""
        response = client.post(
            "/api/plans/generate",
            json={
                "goal_id": 99999,
                "available_hours_per_day": 2
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 2001  # 目标不存在

    def test_get_plan_by_id_success(self, client: TestClient, auth_headers, test_plan):
        """测试获取规划详情"""
        response = client.get(f"/api/plans/{test_plan.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == test_plan.id
        assert "content" in data["data"]

    def test_confirm_plan_success(self, client: TestClient, auth_headers, test_plan):
        """测试确认规划成功"""
        response = client.post(f"/api/plans/{test_plan.id}/confirm", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "tasks_created" in data["data"]
        assert data["message"].startswith("规划确认成功")

    def test_update_plan_success(self, client: TestClient, auth_headers, test_plan):
        """测试修改规划成功"""
        new_content = {
            "stages": [
                {
                    "name": "修改后的阶段",
                    "order": 1,
                    "tasks": [
                        {
                            "title": "修改后的任务",
                            "description": "描述",
                            "estimated_hours": 1.0,
                            "order": 1
                        }
                    ]
                }
            ]
        }

        response = client.put(
            f"/api/plans/{test_plan.id}",
            json=new_content,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "修改成功"

    def test_update_confirmed_plan_should_fail(self, client: TestClient, auth_headers, test_plan):
        """测试修改已确认的规划应该失败"""
        # 先确认规划
        client.post(f"/api/plans/{test_plan.id}/confirm", headers=auth_headers)

        # 尝试修改
        response = client.put(
            f"/api/plans/{test_plan.id}",
            json={"stages": []},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 3002  # 规划已确认，无法修改
