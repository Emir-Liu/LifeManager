"""测试 Timeline API
测试时间线相关的 API 端点
"""
import pytest
from datetime import datetime, timedelta


class TestTimelineAPI:
    """时间线API测试"""

    def test_suggest_task_time(self, client, auth_headers: dict):
        """测试建议任务时间"""
        due_date = datetime.now() + timedelta(days=7)

        response = client.post(
            "/api/timeline/suggest",
            json={
                "task_id": 1,
                "due_date": due_date.isoformat(),
                "duration_minutes": 60
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # 可能成功或失败(取决于任务是否存在)
        assert "code" in data
        assert "message" in data

    def test_auto_assign_task(self, client, auth_headers: dict):
        """测试自动分配任务时间"""
        due_date = datetime.now() + timedelta(days=7)

        response = client.post(
            "/api/timeline/auto-assign",
            json={
                "task_id": 1,
                "due_date": due_date.isoformat(),
                "duration_minutes": 90
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "message" in data

    def test_get_timeline(self, client, auth_headers: dict):
        """测试获取时间线"""
        date_str = datetime.now().strftime("%Y-%m-%d")

        response = client.get(
            f"/api/timeline/{date_str}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "message" in data

    def test_get_timeline_invalid_date_format(self, client, auth_headers: dict):
        """测试获取时间线 - 无效日期格式"""
        response = client.get(
            "/api/timeline/invalid-date",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400
        assert "Invalid date format" in data["message"]

    def test_suggest_task_time_invalid_duration(self, client, auth_headers: dict):
        """测试建议任务时间 - 无效持续时间"""
        due_date = datetime.now() + timedelta(days=7)

        response = client.post(
            "/api/timeline/suggest",
            json={
                "task_id": 1,
                "due_date": due_date.isoformat(),
                "duration_minutes": -60  # 负数
            },
            headers=auth_headers
        )

        # 应该返回验证错误
        assert response.status_code == 422

    def test_auto_assign_task_zero_duration(self, client, auth_headers: dict):
        """测试自动分配任务时间 - 零持续时间"""
        due_date = datetime.now() + timedelta(days=7)

        response = client.post(
            "/api/timeline/auto-assign",
            json={
                "task_id": 1,
                "due_date": due_date.isoformat(),
                "duration_minutes": 0  # 零
            },
            headers=auth_headers
        )

        # 应该返回验证错误
        assert response.status_code == 422
