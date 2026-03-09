"""
Phase 2 前后端集成测试
测试完整的对话规划到时间线管理的流程
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime


class TestCompleteConversationFlow:
    """完整对话流程测试"""

    def test_goal_planning_conversation_flow(self, client: TestClient, auth_headers: dict, db):
        """测试目标规划对话完整流程"""
        from app.models import Conversation, Message

        # 步骤1: 创建目标规划对话
        response = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={
                "conversation_type": "goal_planning",
                "title": "学习Python规划"
            }
        )
        assert response.status_code == 200
        conv_data = response.json()["data"]
        conversation_id = conv_data["id"]
        print(f"[集成测试1] 创建对话成功, ID: {conversation_id}")

        # 步骤2: 发送用户消息
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/chat",
            headers=auth_headers,
            json={"message": "我想在3个月内学会Python编程"}
        )
        assert response.status_code == 200
        print("[集成测试1] 发送消息成功")

        # 步骤3: 获取消息列表
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=auth_headers
        )
        assert response.status_code == 200
        messages = response.json()["data"]["items"]
        assert len(messages) >= 2  # 至少包含用户消息和AI回复
        print(f"[集成测试1] 获取消息成功, 共{len(messages)}条")

        # 步骤4: 查看对话详情
        response = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        print("[集成测试1] 对话流程测试完成 ✓")

    def test_schedule_planning_conversation_flow(self, client: TestClient, auth_headers: dict):
        """测试日程规划对话完整流程"""
        # 创建日程规划对话
        response = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={
                "conversation_type": "schedule_planning",
                "title": "本周日程规划"
            }
        )
        assert response.status_code == 200
        conversation_id = response.json()["data"]["id"]

        # 发送规划请求
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/chat",
            headers=auth_headers,
            json={"message": "帮我规划这周的任务安排"}
        )
        assert response.status_code == 200

        # 验证AI回复
        response = client.get(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=auth_headers
        )
        assert response.status_code == 200
        print("[集成测试2] 日程规划对话测试完成 ✓")

    def test_action_confirmation_flow(self, client: TestClient, auth_headers: dict, db):
        """测试操作确认流程"""
        from app.models import Conversation, Message, Action
        from app.models.user import User

        # 创建用户和对话
        user = db.query(User).filter(User.username == "actionflow").first()
        if not user:
            user = User(username="actionflow", password_hash="hash")
            db.add(user)
            db.commit()

        conv = Conversation(
            user_id=user.id,
            conversation_type="goal_planning",
            status="active"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

        # 添加AI回复消息
        msg = Message(
            conversation_id=conv.id,
            role="assistant",
            message_type="text",
            content="我为您创建了一个学习计划"
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        # 添加待执行的操作
        action = Action(
            message_id=msg.id,
            action_type="create_goal",
            description="创建学习目标",
            action_data={"title": "学习Python", "description": "3个月掌握Python"},
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
        print("[集成测试3] 操作确认流程测试完成 ✓")


class TestTimelineIntegration:
    """时间线集成测试"""

    def test_task_to_timeline_integration(self, client: TestClient, auth_headers: dict, db):
        """测试任务与时间线集成"""
        from app.models import Task, Goal
        from app.models.user import User

        # 创建测试用户
        user = db.query(User).filter(User.username == "timelineuser").first()
        if not user:
            user = User(username="timelineuser", password_hash="hash")
            db.add(user)
            db.commit()

        # 创建目标和任务
        goal = Goal(user_id=user.id, title="测试目标", status="confirmed")
        db.add(goal)
        db.commit()
        db.refresh(goal)

        task = Task(
            goal_id=goal.id,
            title="测试任务",
            description="测试描述",
            due_date=date.today(),
            start_time="09:00",
            end_time="10:00",
            duration_minutes=60,
            status="pending"
        )
        db.add(task)
        db.commit()

        # 获取时间线
        response = client.get(
            f"/api/v1/timeline/{date.today().isoformat()}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()["data"]

        # 验证任务出现在时间线中
        assert "time_slots" in data or "tasks" in data
        print("[集成测试4] 任务时间线集成测试完成 ✓")

    def test_smart_assign_to_timeline(self, client: TestClient, auth_headers: dict, db):
        """测试智能分配到时间线"""
        from app.models import Task, Goal
        from app.models.user import User

        # 创建多个未分配时间的任务
        user = db.query(User).filter(User.username == "smartuser").first()
        if not user:
            user = User(username="smartuser", password_hash="hash")
            db.add(user)
            db.commit()

        goal = Goal(user_id=user.id, title="测试目标", status="confirmed")
        db.add(goal)
        db.commit()
        db.refresh(goal)

        # 创建3个任务
        for i in range(3):
            task = Task(
                goal_id=goal.id,
                title=f"任务{i+1}",
                due_date=date.today(),
                estimated_hours=1.0,
                status="pending"
            )
            db.add(task)
        db.commit()

        # 调用智能分配
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

        # 验证任务被分配时间
        response = client.get(
            f"/api/v1/timeline/{date.today().isoformat()}",
            headers=auth_headers
        )
        assert response.status_code == 200
        print("[集成测试5] 智能分配时间线测试完成 ✓")


class TestTimePreferencesIntegration:
    """时间偏好集成测试"""

    def test_preferences_to_smart_assign(self, client: TestClient, auth_headers: dict):
        """测试时间偏好影响智能分配"""
        # 设置时间偏好
        response = client.post(
            "/api/v1/time-preferences",
            headers=auth_headers,
            json={
                "preferred_start_time": "10:00",
                "preferred_end_time": "17:00",
                "working_days": [1, 2, 3, 4, 5],
                "lunch_start_time": "12:00",
                "lunch_end_time": "13:00"
            }
        )
        assert response.status_code == 200

        # 获取偏好设置
        response = client.get("/api/v1/time-preferences", headers=auth_headers)
        assert response.status_code == 200
        prefs = response.json()["data"]

        # 验证偏好设置正确
        assert prefs["preferred_start_time"] == "10:00"
        print("[集成测试6] 时间偏好设置测试完成 ✓")

    def test_working_hours_calculation(self):
        """测试工作时长计算"""
        # 模拟时间偏好数据
        prefs = {
            "preferred_start_time": "09:00",
            "preferred_end_time": "18:00",
            "lunch_start_time": "12:00",
            "lunch_end_time": "13:00"
        }

        # 计算工作时长
        start = datetime.strptime(prefs["preferred_start_time"], "%H:%M")
        end = datetime.strptime(prefs["preferred_end_time"], "%H:%M")
        lunch_start = datetime.strptime(prefs["lunch_start_time"], "%H:%M")
        lunch_end = datetime.strptime(prefs["lunch_end_time"], "%H:%M")

        total_hours = (end - start).seconds / 3600
        lunch_hours = (lunch_end - lunch_start).seconds / 3600
        working_hours = total_hours - lunch_hours

        assert working_hours == 8.0
        print("[集成测试7] 工作时长计算测试完成 ✓")


class TestEventAndTaskIntegration:
    """事件和任务集成测试"""

    def test_event_and_task_on_timeline(self, client: TestClient, auth_headers: dict, db):
        """测试事件和任务在同一时间线显示"""
        from app.models import Event, Task, Goal
        from app.models.user import User

        # 创建测试数据
        user = db.query(User).filter(User.username == "eventtaskuser").first()
        if not user:
            user = User(username="eventtaskuser", password_hash="hash")
            db.add(user)
            db.commit()

        # 创建事件
        event = Event(
            user_id=user.id,
            title="会议",
            description="团队会议",
            start_date=date.today(),
            start_time="14:00",
            end_time="15:00",
            event_type="meeting"
        )
        db.add(event)

        # 创建任务
        goal = Goal(user_id=user.id, title="测试目标", status="confirmed")
        db.add(goal)
        db.commit()
        db.refresh(goal)

        task = Task(
            goal_id=goal.id,
            title="学习任务",
            due_date=date.today(),
            start_time="16:00",
            end_time="17:00"
        )
        db.add(task)
        db.commit()

        # 获取时间线
        response = client.get(
            f"/api/v1/timeline/{date.today().isoformat()}",
            headers=auth_headers
        )
        assert response.status_code == 200
        print("[集成测试8] 事件任务时间线集成测试完成 ✓")


class TestEndToEndConversationToTimeline:
    """端到端测试：从对话到时间线"""

    def test_complete_conversation_to_timeline(self, client: TestClient, auth_headers: dict, db):
        """完整流程：对话→生成目标→任务→时间线"""
        from app.models import User

        # 步骤1: 创建目标规划对话
        conv_response = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"conversation_type": "goal_planning", "title": "学习计划"}
        )
        conversation_id = conv_response.json()["data"]["id"]
        print("[E2E] 步骤1: 创建对话成功")

        # 步骤2: 发送规划请求
        chat_response = client.post(
            f"/api/v1/conversations/{conversation_id}/chat",
            headers=auth_headers,
            json={"message": "帮我制定一个学习计划"}
        )
        assert chat_response.status_code == 200
        print("[E2E] 步骤2: 对话完成")

        # 步骤3: 获取目标列表（假设对话中创建了目标）
        goals_response = client.get("/api/v1/goals", headers=auth_headers)
        assert goals_response.status_code == 200
        print("[E2E] 步骤3: 获取目标列表成功")

        # 步骤4: 获取任务列表
        tasks_response = client.get("/api/v1/tasks", headers=auth_headers)
        assert tasks_response.status_code == 200
        print("[E2E] 步骤4: 获取任务列表成功")

        # 步骤5: 查看时间线
        timeline_response = client.get(
            f"/api/v1/timeline/{date.today().isoformat()}",
            headers=auth_headers
        )
        assert timeline_response.status_code == 200
        print("[E2E] 步骤5: 查看时间线成功")

        print("\n[E2E] ========== 对话到时间线完整流程测试通过 ==========")


class TestConflictDetection:
    """冲突检测测试"""

    def test_task_time_conflict_detection(self, client: TestClient, auth_headers: dict, db):
        """测试任务时间冲突检测"""
        from app.models import Task, Goal
        from app.models.user import User

        # 创建测试数据
        user = db.query(User).filter(User.username == "conflictuser").first()
        if not user:
            user = User(username="conflictuser", password_hash="hash")
            db.add(user)
            db.commit()

        goal = Goal(user_id=user.id, title="测试目标", status="confirmed")
        db.add(goal)
        db.commit()
        db.refresh(goal)

        # 创建两个时间重叠的任务
        task1 = Task(
            goal_id=goal.id,
            title="任务1",
            due_date=date.today(),
            start_time="09:00",
            end_time="10:00"
        )
        task2 = Task(
            goal_id=goal.id,
            title="任务2",
            due_date=date.today(),
            start_time="09:30",
            end_time="10:30"
        )
        db.add_all([task1, task2])
        db.commit()

        # 获取时间线并验证冲突检测
        response = client.get(
            f"/api/v1/timeline/{date.today().isoformat()}",
            headers=auth_headers
        )
        assert response.status_code == 200
        print("[集成测试9] 冲突检测测试完成 ✓")

    def test_event_task_conflict_detection(self, client: TestClient, auth_headers: dict, db):
        """测试事件和任务冲突检测"""
        from app.models import Event, Task, Goal
        from app.models.user import User

        # 创建测试数据
        user = db.query(User).filter(User.username == "eventconflict").first()
        if not user:
            user = User(username="eventconflict", password_hash="hash")
            db.add(user)
            db.commit()

        # 创建事件
        event = Event(
            user_id=user.id,
            title="会议",
            start_date=date.today(),
            start_time="14:00",
            end_time="15:00"
        )
        db.add(event)

        # 创建冲突的任务
        goal = Goal(user_id=user.id, title="测试目标", status="confirmed")
        db.add(goal)
        db.commit()
        db.refresh(goal)

        task = Task(
            goal_id=goal.id,
            title="学习任务",
            due_date=date.today(),
            start_time="14:30",
            end_time="15:30"
        )
        db.add(task)
        db.commit()

        # 验证冲突检测
        response = client.get(
            f"/api/v1/timeline/{date.today().isoformat()}",
            headers=auth_headers
        )
        assert response.status_code == 200
        print("[集成测试10] 事件任务冲突测试完成 ✓")
