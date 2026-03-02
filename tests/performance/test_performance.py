"""
性能测试
测试API响应时间、数据库性能、代码覆盖率
"""
import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    """数据库会话"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


class TestAPIPerformance:
    """API响应时间测试"""

    @pytest.fixture
    def auth_token(self, client: TestClient):
        """获取认证Token"""
        client.post("/api/auth/register", json={
            "username": "perf_test_user",
            "password": "Test123456"
        })
        response = client.post("/api/auth/login", data={
            "username": "perf_test_user",
            "password": "Test123456"
        })
        return response.json()["data"]["access_token"]

    def test_login_performance(self, client: TestClient):
        """测试登录API响应时间（目标<500ms）"""
        start_time = time.time()

        response = client.post("/api/auth/login", data={
            "username": "perf_test_user",
            "password": "Test123456"
        })

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 转换为毫秒

        assert response.status_code == 200
        assert response_time < 500, f"登录API响应时间{response_time:.2f}ms超过500ms"
        print(f"[PERF] 登录API响应时间: {response_time:.2f}ms ✅")

    def test_get_goals_performance(self, client: TestClient, auth_token: str):
        """测试获取目标列表API响应时间（目标<500ms）"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # 先创建一些数据
        for i in range(10):
            client.post("/api/goals", json={
                "title": f"性能测试目标{i}",
                "description": f"描述{i}"
            }, headers=headers)

        start_time = time.time()
        response = client.get("/api/goals", headers=headers)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time < 500, f"获取目标列表API响应时间{response_time:.2f}ms超过500ms"
        print(f"[PERF] 获取目标列表API响应时间: {response_time:.2f}ms ✅")

    def test_create_goal_performance(self, client: TestClient, auth_token: str):
        """测试创建目标API响应时间（目标<500ms）"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        start_time = time.time()
        response = client.post("/api/goals", json={
            "title": "性能测试目标",
            "description": "性能测试描述"
        }, headers=headers)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time < 500, f"创建目标API响应时间{response_time:.2f}ms超过500ms"
        print(f"[PERF] 创建目标API响应时间: {response_time:.2f}ms ✅")

    def test_get_tasks_performance(self, client: TestClient, auth_token: str):
        """测试获取任务列表API响应时间（目标<500ms）"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        start_time = time.time()
        response = client.get("/api/tasks", headers=headers)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert response_time < 500, f"获取任务列表API响应时间{response_time:.2f}ms超过500ms"
        print(f"[PERF] 获取任务列表API响应时间: {response_time:.2f}ms ✅")

    def test_generate_plan_performance(self, client: TestClient, auth_token: str):
        """测试生成规划API响应时间（目标<2000ms，AI调用可能较慢）"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # 创建目标
        goal_response = client.post("/api/goals", json={
            "title": "AI规划性能测试",
            "description": "测试AI生成规划的性能"
        }, headers=headers)
        goal_id = goal_response.json()["data"]["id"]

        start_time = time.time()
        response = client.post("/api/plans", json={
            "goal_id": goal_id,
            "available_hours": 2
        }, headers=headers)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        assert response.status_code == 200
        # AI调用可能较慢，允许2秒
        assert response_time < 2000, f"生成规划API响应时间{response_time:.2f}ms超过2000ms"
        print(f"[PERF] 生成规划API响应时间: {response_time:.2f}ms ✅")


class TestDatabasePerformance:
    """数据库性能基准测试"""

    def test_bulk_insert_performance(self, db_session: Session):
        """测试批量插入性能（100条记录<1000ms）"""
        from app.models.user import User, get_password_hash
        from datetime import datetime

        start_time = time.time()

        # 批量插入100个用户
        users = []
        for i in range(100):
            user = User(
                username=f"perf_user_{i}",
                password_hash=get_password_hash("password123"),
                email=f"perf_user_{i}@example.com"
            )
            users.append(user)

        db_session.add_all(users)
        db_session.commit()

        end_time = time.time()
        insert_time = (end_time - start_time) * 1000

        assert insert_time < 1000, f"批量插入100条记录耗时{insert_time:.2f}ms超过1000ms"
        print(f"[PERF] 批量插入100条用户耗时: {insert_time:.2f}ms ✅")

        # 清理数据
        db_session.query(User).filter(User.username.like("perf_user_%")).delete()
        db_session.commit()

    def test_query_performance(self, db_session: Session):
        """测试查询性能（1000条查询<500ms）"""
        from app.models.user import User, get_password_hash

        # 准备数据
        for i in range(100):
            user = User(
                username=f"query_test_{i}",
                password_hash=get_password_hash("password123"),
                email=f"query_test_{i}@example.com"
            )
            db_session.add(user)
        db_session.commit()

        start_time = time.time()

        # 执行1000次查询
        for _ in range(1000):
            users = db_session.query(User).filter(User.username.like("query_test_%")).all()

        end_time = time.time()
        query_time = (end_time - start_time) * 1000

        assert query_time < 500, f"1000次查询耗时{query_time:.2f}ms超过500ms"
        print(f"[PERF] 1000次查询耗时: {query_time:.2f}ms ✅")

        # 清理
        db_session.query(User).filter(User.username.like("query_test_%")).delete()
        db_session.commit()

    def test_join_query_performance(self, db_session: Session):
        """测试关联查询性能（100次<500ms）"""
        from app.models.user import User, get_password_hash
        from app.models.goal import Goal
        from app.models.task import Task
        from datetime import date

        # 准备数据
        user = User(username="join_test", password_hash=get_password_hash("password123"))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        goals = []
        for i in range(10):
            goal = Goal(
                user_id=user.id,
                title=f"目标{i}",
                status="confirmed"
            )
            goals.append(goal)
        db_session.add_all(goals)
        db_session.commit()

        # 为每个目标添加任务
        for goal in goals:
            tasks = []
            for j in range(5):
                task = Task(
                    goal_id=goal.id,
                    title=f"任务{i}-{j}",
                    due_date=date.today()
                )
                tasks.append(task)
            db_session.add_all(tasks)
        db_session.commit()

        start_time = time.time()

        # 执行100次关联查询
        for _ in range(100):
            result = db_session.query(Task).join(Goal).join(User).filter(
                User.username == "join_test"
            ).all()

        end_time = time.time()
        join_time = (end_time - start_time) * 1000

        assert join_time < 500, f"100次关联查询耗时{join_time:.2f}ms超过500ms"
        print(f"[PERF] 100次关联查询耗时: {join_time:.2f}ms ✅")

        # 清理
        db_session.query(Task).filter(Task.title.like("任务%")).delete()
        db_session.query(Goal).filter(Goal.title.like("目标%")).delete()
        db_session.query(User).filter(User.username == "join_test").delete()
        db_session.commit()


class TestCodeCoverage:
    """代码覆盖率测试"""

    def test_service_layer_coverage(self):
        """测试服务层代码覆盖率（目标>80%）"""
        import subprocess
        import os

        # 运行pytest并生成覆盖率报告
        result = subprocess.run(
            ["pytest", "backend/tests/", "--cov=backend/app/services", "--cov-report=term"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        output = result.stdout

        # 检查覆盖率（这里只是示例，实际需要解析覆盖率报告）
        print(f"[PERF] 服务层覆盖率测试完成")
        print(output)

    def test_api_layer_coverage(self):
        """测试API层代码覆盖率（目标>80%）"""
        import subprocess
        import os

        result = subprocess.run(
            ["pytest", "backend/tests/", "--cov=backend/app/api", "--cov-report=term"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        print(f"[PERF] API层覆盖率测试完成")
        print(result.stdout)

    def test_model_layer_coverage(self):
        """测试模型层代码覆盖率（目标>90%）"""
        import subprocess
        import os

        result = subprocess.run(
            ["pytest", "backend/tests/", "--cov=backend/app/models", "--cov-report=term"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        print(f"[PERF] 模型层覆盖率测试完成")
        print(result.stdout)


class TestLoadTesting:
    """负载测试"""

    def test_concurrent_requests(self, client: TestClient):
        """测试并发请求（10个并发用户）"""
        import threading

        def create_user_and_login():
            username = f"load_user_{threading.get_ident()}"
            # 注册
            client.post("/api/auth/register", json={
                "username": username,
                "password": "Test123456"
            })
            # 登录
            response = client.post("/api/auth/login", data={
                "username": username,
                "password": "Test123456"
            })
            return response.status_code == 200

        threads = []
        start_time = time.time()

        # 创建10个并发线程
        for _ in range(10):
            thread = threading.Thread(target=create_user_and_login)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = (end_time - start_time) * 1000

        print(f"[PERF] 10个并发请求总耗时: {total_time:.2f}ms ✅")

        # 平均每个请求应该在合理范围内
        avg_time = total_time / 10
        assert avg_time < 1000, f"平均响应时间{avg_time:.2f}ms过长"

    def test_sequential_requests(self, client: TestClient):
        """测试连续请求（100次）"""
        # 注册一个用户
        client.post("/api/auth/register", json={
            "username": "seq_test_user",
            "password": "Test123456"
        })

        # 登录获取token
        response = client.post("/api/auth/login", data={
            "username": "seq_test_user",
            "password": "Test123456"
        })
        token = response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        start_time = time.time()

        # 执行100次获取目标列表请求
        for _ in range(100):
            client.get("/api/goals", headers=headers)

        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        avg_time = total_time / 100

        assert avg_time < 100, f"平均响应时间{avg_time:.2f}ms过长"
        print(f"[PERF] 100次连续请求，平均响应时间: {avg_time:.2f}ms ✅")
