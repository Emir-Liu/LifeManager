"""
Phase 2 后端单元测试
测试对话、时间线、时间偏好等Phase 2新增功能
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date, time
from sqlalchemy.orm import Session


class TestConversationAPI:
    """对话API测试"""

    def test_create_conversation(self, client: TestClient, auth_headers: dict):
        """测试创建对话"""
        response = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={
                "conversation_type": "goal_planning",
                "title": "目标规划对话"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "id" in data["data"]
        assert data["data"]["title"] == "目标规划对话"

    def test_list_conversations(self, client: TestClient, auth_headers: dict):
        """测试获取对话列表"""
        # 创建对话
        client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"conversation_type": "general_chat"}
        )

        # 获取列表
        response = client.get("/api/v1/conversations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]["items"]) > 0

    def test_send_message(self, client: TestClient, auth_headers: dict, db: Session):
        """测试发送消息"""
        from app.models import Conversation
        from app.models.user import User

        # 获取用户
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(username="testuser", password_hash="hash", email="test@example.com")
            db.add(user)
            db.commit()

        # 创建对话
        conv = Conversation(
            user_id=user.id,
            conversation_type="general_chat",
            status="active"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

        # 发送消息
        response = client.post(
            f"/api/v1/conversations/{conv.id}/chat",
            headers=auth_headers,
            json={"message": "你好"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "ai_message" in data["data"]

    def test_get_conversation_messages(self, client: TestClient, auth_headers: dict, db: Session):
        """测试获取对话消息"""
        from app.models import Conversation, Message
        from app.models.user import User

        # 创建用户和对话
        user = db.query(User).filter(User.username == "msgtest").first()
        if not user:
            user = User(username="msgtest", password_hash="hash", email="msgtest@example.com")
            db.add(user)
            db.commit()

        conv = Conversation(user_id=user.id, conversation_type="general_chat", status="active")
        db.add(conv)
        db.commit()
        db.refresh(conv)

        # 添加消息
        msg = Message(
            conversation_id=conv.id,
            role="user",
            message_type="text",
            content="测试消息"
        )
        db.add(msg)
        db.commit()

        # 获取消息
        response = client.get(f"/api/v1/conversations/{conv.id}/messages", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]["items"]) > 0

    def test_execute_action(self, client: TestClient, auth_headers: dict, db: Session):
        """测试执行操作"""
        from app.models import Conversation, Message, Action
        from app.models.user import User

        # 创建测试数据
        user = db.query(User).filter(User.username == "actiontest").first()
        if not user:
            user = User(username="actiontest", password_hash="hash")
            db.add(user)
            db.commit()

        conv = Conversation(user_id=user.id, conversation_type="goal_planning", status="active")
        db.add(conv)
        db.commit()
        db.refresh(conv)

        msg = Message(
            conversation_id=conv.id,
            role="assistant",
            message_type="text",
            content="创建了一个目标"
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        action = Action(
            message_id=msg.id,
            action_type="create_goal",
            description="创建学习Python的目标",
            action_data={"title": "学习Python", "description": "掌握Python编程"},
            status="pending"
        )
        db.add(action)
        db.commit()

        # 执行操作
        response = client.put(
            f"/api/v1/conversations/actions/{action.id}",
            headers=auth_headers,
            json={"status": "executed"}
        )
        assert response.status_code == 200


class TestTimelineAPI:
    """时间线API测试"""

    def test_get_timeline(self, client: TestClient, auth_headers: dict):
        """测试获取时间线"""
        test_date = date.today().isoformat()
        response = client.get(f"/api/v1/timeline/{test_date}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "time_slots" in data["data"]

    def test_smart_assign_tasks(self, client: TestClient, auth_headers: dict):
        """测试智能分配任务"""
        response = client.post(
            "/api/v1/timeline/smart-assign",
            headers=auth_headers,
            json={
                "date_range": {
                    "start_date": date.today().isoformat(),
                    "end_date": date.today().isoformat()
                },
                "preferences": {
                    "preferred_time": "09:00-18:00"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_get_timeline_stats(self, client: TestClient, auth_headers: dict):
        """测试获取时间线统计"""
        response = client.get("/api/v1/timeline/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestTimePreferencesAPI:
    """时间偏好API测试"""

    def test_get_preferences(self, client: TestClient, auth_headers: dict):
        """测试获取时间偏好"""
        response = client.get("/api/v1/time-preferences", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_create_preferences(self, client: TestClient, auth_headers: dict):
        """测试创建时间偏好"""
        response = client.post(
            "/api/v1/time-preferences",
            headers=auth_headers,
            json={
                "preferred_start_time": "09:00",
                "preferred_end_time": "18:00",
                "lunch_start_time": "12:00",
                "lunch_end_time": "13:00",
                "working_days": [1, 2, 3, 4, 5]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_update_preferences(self, client: TestClient, auth_headers: dict):
        """测试更新时间偏好"""
        # 先创建
        create_resp = client.post(
            "/api/v1/time-preferences",
            headers=auth_headers,
            json={
                "preferred_start_time": "09:00",
                "preferred_end_time": "18:00",
                "working_days": [1, 2, 3, 4, 5]
            }
        )

        # 获取ID并更新
        if create_resp.status_code == 200:
            pref_id = create_resp.json()["data"].get("id") or 1
            response = client.put(
                f"/api/v1/time-preferences/{pref_id}",
                headers=auth_headers,
                json={
                    "preferred_start_time": "10:00",
                    "preferred_end_time": "19:00"
                }
            )
            assert response.status_code == 200


class TestTaskEnhancements:
    """任务增强功能测试"""

    def test_create_task_with_time(self, client: TestClient, auth_headers: dict):
        """测试创建带具体时间的任务"""
        response = client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={
                "title": "测试任务",
                "description": "测试描述",
                "due_date": date.today().isoformat(),
                "start_time": "09:00",
                "end_time": "10:00",
                "duration_minutes": 60,
                "task_type": "work"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["start_time"] == "09:00"

    def test_update_task_time(self, client: TestClient, auth_headers: dict, db: Session):
        """测试更新任务时间"""
        from app.models import Task, Goal
        from app.models.user import User

        # 创建测试数据
        user = db.query(User).filter(User.username == "timetask").first()
        if not user:
            user = User(username="timetask", password_hash="hash")
            db.add(user)
            db.commit()

        goal = Goal(user_id=user.id, title="测试目标", status="confirmed")
        db.add(goal)
        db.commit()
        db.refresh(goal)

        task = Task(
            goal_id=goal.id,
            title="测试任务",
            due_date=date.today(),
            start_time="09:00",
            end_time="10:00"
        )
        db.add(task)
        db.commit()

        # 更新任务时间
        response = client.put(
            f"/api/v1/tasks/{task.id}",
            headers=auth_headers,
            json={
                "start_time": "14:00",
                "end_time": "15:00"
            }
        )
        assert response.status_code == 200


class TestEventManagement:
    """日程事件管理测试"""

    def test_create_event(self, client: TestClient, auth_headers: dict):
        """测试创建日程事件"""
        response = client.post(
            "/api/v1/events",
            headers=auth_headers,
            json={
                "title": "会议",
                "description": "团队会议",
                "start_date": date.today().isoformat(),
                "start_time": "14:00",
                "end_time": "15:00",
                "event_type": "meeting"
            }
        )
        assert response.status_code == 200

    def test_list_events(self, client: TestClient, auth_headers: dict):
        """测试获取日程事件列表"""
        response = client.get("/api/v1/events", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_update_event(self, client: TestClient, auth_headers: dict, db: Session):
        """测试更新日程事件"""
        from app.models import Event
        from app.models.user import User

        user = db.query(User).filter(User.username == "eventtest").first()
        if not user:
            user = User(username="eventtest", password_hash="hash")
            db.add(user)
            db.commit()

        event = Event(
            user_id=user.id,
            title="原始会议",
            start_date=date.today(),
            start_time="14:00",
            end_time="15:00"
        )
        db.add(event)
        db.commit()

        # 更新事件
        response = client.put(
            f"/api/v1/events/{event.id}",
            headers=auth_headers,
            json={"title": "更新后的会议"}
        )
        assert response.status_code == 200

    def test_delete_event(self, client: TestClient, auth_headers: dict, db: Session):
        """测试删除日程事件"""
        from app.models import Event
        from app.models.user import User

        user = db.query(User).filter(User.username == "eventdel").first()
        if not user:
            user = User(username="eventdel", password_hash="hash")
            db.add(user)
            db.commit()

        event = Event(
            user_id=user.id,
            title="待删除会议",
            start_date=date.today(),
            start_time="14:00",
            end_time="15:00"
        )
        db.add(event)
        db.commit()

        # 删除事件
        response = client.delete(f"/api/v1/events/{event.id}", headers=auth_headers)
        assert response.status_code == 200
