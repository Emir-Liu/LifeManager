"""测试 Event API
测试日程相关的 API 端点
"""
import pytest
from datetime import datetime, timedelta, date


class TestEventAPI:
    """日程API测试"""

    def test_create_event_success(self, client, auth_headers: dict):
        """测试成功创建日程"""
        start_date = date.today() + timedelta(days=1)
        start_time = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=9)
        end_time = start_time + timedelta(hours=1)

        response = client.post(
            "/api/events",
            json={
                "title": "测试日程",
                "event_type": "meeting",
                "start_date": start_date.isoformat(),
                "end_date": start_date.isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": 60,
                "description": "这是一个测试日程"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["title"] == "测试日程"

    def test_create_event_invalid_time(self, client, auth_headers: dict):
        """测试创建时间无效的日程"""
        start_date = date.today() + timedelta(days=1)
        start_time = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=10)
        end_time = start_time - timedelta(hours=1)  # 结束时间早于开始时间

        response = client.post(
            "/api/events",
            json={
                "title": "无效日程",
                "event_type": "meeting",
                "start_date": start_date.isoformat(),
                "end_date": start_date.isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": 60
            },
            headers=auth_headers
        )

        # 应该返回错误
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0

    def test_get_events_list(self, client, auth_headers: dict):
        """测试获取日程列表"""
        response = client.get(
            "/api/events",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)

    def test_get_events_with_date_range(self, client, auth_headers: dict):
        """测试按日期范围获取日程"""
        start_date = (date.today() - timedelta(days=7)).isoformat()
        end_date = (date.today() + timedelta(days=7)).isoformat()

        response = client.get(
            f"/api/events?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data

    def test_get_event_by_id(self, client, auth_headers: dict):
        """测试获取单个日程详情"""
        # 创建日程
        start_date = date.today() + timedelta(days=1)
        start_time = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=9)
        end_time = start_time + timedelta(hours=1)
        create_resp = client.post(
            "/api/events",
            json={
                "title": "日程详情测试",
                "event_type": "task",
                "start_date": start_date.isoformat(),
                "end_date": start_date.isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": 60
            },
            headers=auth_headers
        )
        event_id = create_resp.json()["data"]["id"]

        response = client.get(
            f"/api/events/{event_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == event_id

    def test_update_event(self, client, auth_headers: dict):
        """测试更新日程"""
        # 创建日程
        start_date = date.today() + timedelta(days=1)
        start_time = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=9)
        end_time = start_time + timedelta(hours=1)
        create_resp = client.post(
            "/api/events",
            json={
                "title": "更新前",
                "event_type": "meeting",
                "start_date": start_date.isoformat(),
                "end_date": start_date.isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": 60
            },
            headers=auth_headers
        )
        event_id = create_resp.json()["data"]["id"]

        response = client.put(
            f"/api/events/{event_id}",
            json={"title": "更新后", "description": "新的描述"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "更新后"

    def test_delete_event(self, client, auth_headers: dict):
        """测试删除日程"""
        # 创建日程
        start_date = date.today() + timedelta(days=1)
        start_time = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=9)
        end_time = start_time + timedelta(hours=1)
        create_resp = client.post(
            "/api/events",
            json={
                "title": "删除测试",
                "event_type": "task",
                "start_date": start_date.isoformat(),
                "end_date": start_date.isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": 60
            },
            headers=auth_headers
        )
        event_id = create_resp.json()["data"]["id"]

        response = client.delete(
            f"/api/events/{event_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "删除成功"

    def test_get_event_not_found(self, client, auth_headers: dict):
        """测试获取不存在的日程"""
        response = client.get(
            "/api/events/99999",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404
