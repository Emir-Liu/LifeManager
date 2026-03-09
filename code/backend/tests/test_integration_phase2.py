"""
Phase 2 Integration Tests
Phase 2 集成测试 - 完整业务流程测试
"""
import pytest
from datetime import date, time, datetime


class TestPhase2Integration:
    """Phase 2 集成测试类"""

    def test_complete_scheduling_workflow(self, client, auth_headers, test_goal):
        """测试完整调度工作流"""
        # 1. 创建时间偏好
        pref_resp = client.post(
            "/api/v1/time-preferences",
            json={
                "sleep_type": "normal",
                "wake_up_time": "07:00:00",
                "sleep_time": "23:00:00",
                "lunch_start": "12:00:00",
                "lunch_end": "13:30:00",
                "work_start": "09:00:00",
                "work_end": "18:00:00",
                "work_days": "0,1,2,3,4"
            },
            headers=auth_headers
        )
        assert pref_resp.status_code == 201

        # 2. 创建日程
        event_resp = client.post(
            "/api/v1/events",
            json={
                "title": "团队会议",
                "description": "每周例会",
                "event_type": "meeting",
                "start_date": "2026-03-10",
                "start_time": "14:00:00",
                "end_time": "16:00:00"
            },
            headers=auth_headers
        )
        assert event_resp.status_code == 201

        # 3. 创建任务
        task_resp = client.post(
            "/api/v1/tasks",
            json={
                "goal_id": test_goal.id,
                "title": "学习Python",
                "description": "完成Python基础学习",
                "due_date": "2026-03-10",
                "estimated_hours": 2
            },
            headers=auth_headers
        )
        assert task_resp.status_code == 201
        task_id = task_resp.json()["id"]

        # 4. 获取时间建议
        suggest_resp = client.post(
            "/api/v1/timeline/suggest",
            json={
                "duration_minutes": 120,
                "due_date": "2026-03-10"
            },
            headers=auth_headers
        )
        assert suggest_resp.status_code == 200
        suggest_data = suggest_resp.json()
        assert suggest_data["success"] == True
        assert len(suggest_data["time_slots"]) > 0

        # 5. 自动分配任务
        assign_resp = client.post(
            f"/api/v1/timeline/auto-assign/{task_id}",
            json={"due_date": "2026-03-10"},
            headers=auth_headers
        )
        assert assign_resp.status_code == 200

        # 6. 获取时间线验证
        timeline_resp = client.get(
            "/api/v1/timeline",
            params={"date": "2026-03-10"},
            headers=auth_headers
        )
        assert timeline_resp.status_code == 200
        timeline_data = timeline_resp.json()
        assert "time_slots" in timeline_data

    def test_conversation_with_action(self, client, auth_headers, test_goal):
        """测试对话和操作执行"""
        # 1. 创建对话
        conv_resp = client.post(
            "/api/v1/conversations",
            json={
                "title": "任务规划对话",
                "context": "任务规划"
            },
            headers=auth_headers
        )
        assert conv_resp.status_code == 201
        conv_id = conv_resp.json()["id"]

        # 2. 发送消息
        msg_resp = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={
                "content": "帮我安排明天下午2点到4点学习Python"
            },
            headers=auth_headers
        )
        assert msg_resp.status_code == 201

        # 3. 获取消息列表
        list_resp = client.get(
            f"/api/v1/conversations/{conv_id}/messages",
            headers=auth_headers
        )
        assert list_resp.status_code == 200
        messages = list_resp.json()["messages"]
        assert len(messages) >= 1

    def test_conflict_detection_workflow(self, client, auth_headers):
        """测试冲突检测工作流"""
        # 1. 创建时间偏好
        client.post(
            "/api/v1/time-preferences",
            json={
                "sleep_type": "normal",
                "wake_up_time": "07:00:00",
                "sleep_time": "23:00:00",
                "work_start": "09:00:00",
                "work_end": "18:00:00"
            },
            headers=auth_headers
        )

        # 2. 创建第一个日程
        event1_resp = client.post(
            "/api/v1/events",
            json={
                "title": "重要会议",
                "event_type": "meeting",
                "start_date": "2026-03-10",
                "start_time": "14:00:00",
                "end_time": "16:00:00"
            },
            headers=auth_headers
        )
        assert event1_resp.status_code == 201

        # 3. 获取时间线,验证冲突检测
        timeline_resp = client.get(
            "/api/v1/timeline",
            params={"date": "2026-03-10"},
            headers=auth_headers
        )
        assert timeline_resp.status_code == 200
        timeline_data = timeline_resp.json()

        # 验证会议时间段被标记为不可用
        meeting_slots = [
            slot for slot in timeline_data["time_slots"]
            if "重要会议" in (slot.get("event") or "")
        ]
        assert len(meeting_slots) > 0

    def test_multi_task_scheduling(self, client, auth_headers, test_goal):
        """测试多任务调度"""
        # 创建时间偏好
        client.post(
            "/api/v1/time-preferences",
            json={
                "sleep_type": "normal",
                "wake_up_time": "07:00:00",
                "sleep_time": "23:00:00",
                "work_start": "09:00:00",
                "work_end": "18:00:00"
            },
            headers=auth_headers
        )

        # 创建多个任务
        tasks = []
        for i in range(3):
            resp = client.post(
                "/api/v1/tasks",
                json={
                    "goal_id": test_goal.id,
                    "title": f"任务{i+1}",
                    "description": f"这是任务{i+1}",
                    "due_date": "2026-03-10",
                    "estimated_hours": 1
                },
                headers=auth_headers
            )
            assert resp.status_code == 201
            tasks.append(resp.json()["id"])

        # 自动分配所有任务
        for task_id in tasks:
            resp = client.post(
                f"/api/v1/timeline/auto-assign/{task_id}",
                json={"due_date": "2026-03-10"},
                headers=auth_headers
            )
            # 任务可能成功分配,也可能因为时间不足而失败
            assert resp.status_code == 200

        # 获取最终时间线
        timeline_resp = client.get(
            "/api/v1/timeline",
            params={"date": "2026-03-10"},
            headers=auth_headers
        )
        assert timeline_resp.status_code == 200

    def test_date_range_timeline(self, client, auth_headers):
        """测试日期范围时间线"""
        # 创建不同日期的日程
        dates = ["2026-03-10", "2026-03-11", "2026-03-12"]
        for i, date_str in enumerate(dates):
            client.post(
                "/api/v1/events",
                json={
                    "title": f"日程{i+1}",
                    "event_type": "meeting",
                    "start_date": date_str,
                    "start_time": "10:00:00",
                    "end_time": "11:00:00"
                },
                headers=auth_headers
            )

        # 获取范围内的时间线
        for date_str in dates:
            resp = client.get(
                "/api/v1/timeline",
                params={"date": date_str},
                headers=auth_headers
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["date"] == date_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
