"""测试 TimePreference API
测试时间偏好相关的 API 端点
"""
import pytest


class TestTimePreferenceAPI:
    """时间偏好API测试"""

    def test_create_time_preference(self, client, auth_headers: dict):
        """测试创建时间偏好"""
        response = client.post(
            "/api/time-preferences",
            json={
                "preferred_start_time": "09:00",
                "preferred_end_time": "18:00",
                "break_duration": 60,
                "max_continuous_work": 120
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "id" in data["data"]

    def test_get_time_preference(self, client, auth_headers: dict):
        """测试获取时间偏好"""
        response = client.get(
            "/api/time-preferences",
            headers=auth_headers
        )

        # 可能返回404(如果没有创建过)或200
        assert response.status_code == 200
        data = response.json()
        if data["code"] == 0:
            assert "data" in data
        else:
            assert data["code"] == 404

    def test_update_time_preference(self, client, auth_headers: dict):
        """测试更新时间偏好"""
        # 先创建
        client.post(
            "/api/time-preferences",
            json={
                "preferred_start_time": "09:00",
                "preferred_end_time": "18:00"
            },
            headers=auth_headers
        )

        response = client.put(
            "/api/time-preferences",
            json={
                "preferred_start_time": "10:00",
                "preferred_end_time": "19:00",
                "break_duration": 90
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data

    def test_get_time_stats(self, client, auth_headers: dict):
        """测试获取时间统计"""
        from datetime import datetime, timedelta

        start_date = (datetime.now().date() - timedelta(days=7)).isoformat()
        end_date = (datetime.now().date()).isoformat()

        response = client.get(
            f"/api/time-preferences/stats?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data

    def test_create_invalid_time_preference(self, client, auth_headers: dict):
        """测试创建无效的时间偏好"""
        response = client.post(
            "/api/time-preferences",
            json={
                "preferred_start_time": "18:00",
                "preferred_end_time": "09:00"  # 结束时间早于开始时间
            },
            headers=auth_headers
        )

        # 应该返回错误
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0
