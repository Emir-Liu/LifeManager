"""
更多集成测试用例
"""
import pytest
from datetime import date, timedelta


class TestUserStatistics:
    """用户统计集成测试"""

    def test_goal_statistics(self, client, test_user, auth_headers):
        """测试目标统计"""
        # 创建多个目标
        for i in range(3):
            client.post(
                "/api/goals",
                json={
                    "title": f"目标{i}",
                    "description": f"描述{i}"
                },
                headers=auth_headers
            )

        # 获取统计
        response = client.get("/api/goals/statistics", headers=auth_headers)
        assert response.status_code == 200
        stats = response.json()["data"]
        assert stats["total"] == 3

    def test_task_statistics(self, client, test_user, auth_headers, test_goal):
        """测试任务统计"""
        from app.models import Task

        # 创建多个任务
        for i in range(5):
            task = Task(
                goal_id=test_goal.id,
                title=f"任务{i}",
                description=f"描述{i}",
                due_date=date.today() + timedelta(days=i),
                completed=(i % 2 == 0)
            )
            client.post(
                "/api/tasks",
                json={
                    "goal_id": test_goal.id,
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat()
                },
                headers=auth_headers
            )

        # 获取任务统计
        response = client.get("/api/tasks/statistics", headers=auth_headers)
        assert response.status_code == 200
        stats = response.json()["data"]
        assert stats["total"] >= 5


class TestPlanFlow:
    """规划流程集成测试"""

    def test_plan_lifecycle(self, client, test_user, auth_headers, test_goal):
        """测试规划完整生命周期"""
        # 1. 生成规划
        response = client.post(
            "/api/plans",
            json={
                "goal_id": test_goal.id,
                "available_hours": 2
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        plan_id = response.json()["data"]["id"]

        # 2. 获取规划
        response = client.get(f"/api/plans/{plan_id}", headers=auth_headers)
        assert response.status_code == 200
        plan = response.json()["data"]
        assert plan["status"] == "draft"

        # 3. 更新规划
        response = client.put(
            f"/api/plans/{plan_id}",
            json={"content": '{"stages": []}'},
            headers=auth_headers
        )
        assert response.status_code == 200

        # 4. 确认规划
        response = client.post(f"/api/plans/{plan_id}/confirm", headers=auth_headers)
        assert response.status_code == 200
        confirmed_plan = response.json()["data"]
        assert confirmed_plan["status"] == "confirmed"


class TestTaskFlow:
    """任务流程集成测试"""

    def test_task_complete_flow(self, client, test_user, auth_headers, test_goal):
        """测试任务完成流程"""
        # 创建任务
        response = client.post(
            "/api/tasks",
            json={
                "goal_id": test_goal.id,
                "title": "学习Python",
                "description": "掌握Python基础",
                "due_date": (date.today() + timedelta(days=7)).isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        task_id = response.json()["data"]["id"]

        # 完成任务
        response = client.put(f"/api/tasks/{task_id}/complete", headers=auth_headers)
        assert response.status_code == 200
        task = response.json()["data"]
        assert task["completed"] is True

        # 取消完成
        response = client.put(f"/api/tasks/{task_id}/uncomplete", headers=auth_headers)
        assert response.status_code == 200
        task = response.json()["data"]
        assert task["completed"] is False

    def test_task_delete_flow(self, client, test_user, auth_headers, test_goal):
        """测试任务删除流程"""
        # 创建任务
        response = client.post(
            "/api/tasks",
            json={
                "goal_id": test_goal.id,
                "title": "学习Python",
                "due_date": date.today().isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        task_id = response.json()["data"]["id"]

        # 删除任务
        response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 200

        # 验证已删除
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 404


class TestEdgeCases:
    """边界条件集成测试"""

    def test_long_title(self, client, test_user, auth_headers):
        """测试超长标题"""
        long_title = "a" * 200  # 200个字符

        response = client.post(
            "/api/goals",
            json={
                "title": long_title,
                "description": "测试"
            },
            headers=auth_headers
        )

        # 根据实际验证规则调整断言
        assert response.status_code in [200, 422]

    def test_empty_description(self, client, test_user, auth_headers):
        """测试空描述"""
        response = client.post(
            "/api/goals",
            json={
                "title": "学习Python",
                "description": ""
            },
            headers=auth_headers
        )

        # 空描述应该被接受
        assert response.status_code == 200

    def test_past_due_date(self, client, test_user, auth_headers, test_goal):
        """测试过期日期"""
        response = client.post(
            "/api/tasks",
            json={
                "goal_id": test_goal.id,
                "title": "学习Python",
                "due_date": (date.today() - timedelta(days=1)).isoformat()
            },
            headers=auth_headers
        )

        # 过期日期应该被接受
        assert response.status_code == 200


class TestDataConsistency:
    """数据一致性集成测试"""

    def test_goal_task_relationship(self, client, test_user, auth_headers, test_goal):
        """测试目标和任务关系"""
        # 创建任务
        client.post(
            "/api/tasks",
            json={
                "goal_id": test_goal.id,
                "title": "任务1",
                "due_date": date.today().isoformat()
            },
            headers=auth_headers
        )

        # 获取目标任务
        response = client.get(f"/api/tasks?goal_id={test_goal.id}", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()["data"]
        assert len(tasks) >= 1
        assert tasks[0]["goal_id"] == test_goal.id

    def test_cascade_delete(self, client, test_user, auth_headers):
        """测试级联删除"""
        # 创建目标
        goal_response = client.post(
            "/api/goals",
            json={
                "title": "测试目标",
                "description": "测试"
            },
            headers=auth_headers
        )
        goal_id = goal_response.json()["data"]["id"]

        # 创建任务
        task_response = client.post(
            "/api/tasks",
            json={
                "goal_id": goal_id,
                "title": "任务1",
                "due_date": date.today().isoformat()
            },
            headers=auth_headers
        )
        task_id = task_response.json()["data"]["id"]

        # 删除目标
        client.delete(f"/api/goals/{goal_id}", headers=auth_headers)

        # 验证任务也被删除
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 404


class TestConcurrency:
    """并发场景集成测试"""

    def test_concurrent_goal_creation(self, client, test_user, auth_headers):
        """测试并发创建目标"""
        import threading

        def create_goal(index):
            client.post(
                "/api/goals",
                json={
                    "title": f"并发目标{index}",
                    "description": f"描述{index}"
                },
                headers=auth_headers
            )

        # 创建10个并发线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_goal, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证所有目标都创建了
        response = client.get("/api/goals", headers=auth_headers)
        assert response.status_code == 200
        goals = response.json()["data"]
        assert len(goals) >= 10


class TestErrorHandling:
    """错误处理集成测试"""

    def test_invalid_goal_id(self, client, test_user, auth_headers):
        """测试无效目标ID"""
        response = client.get("/api/goals/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_invalid_plan_id(self, client, test_user, auth_headers):
        """测试无效规划ID"""
        response = client.get("/api/plans/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_invalid_task_id(self, client, test_user, auth_headers):
        """测试无效任务ID"""
        response = client.get("/api/tasks/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_missing_auth_header(self, client):
        """测试缺少认证头"""
        response = client.get("/api/goals")
        assert response.status_code == 401

    def test_invalid_token(self, client):
        """测试无效token"""
        response = client.get(
            "/api/goals",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
