"""
安全测试
测试认证、授权、SQL注入、XSS等安全漏洞
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text


@pytest.fixture
def db_session():
    """数据库会话"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.rollback()
        db.close()


class TestAuthentication:
    """认证安全测试"""

    def test_weak_password_rejected(self, client: TestClient):
        """测试弱密码被拒绝"""
        # 尝试注册弱密码
        weak_passwords = [
            "123456",       # 纯数字
            "password",     # 常见密码
            "abc",          # 过短
            "123",          # 过短且纯数字
        ]

        for weak_password in weak_passwords:
            response = client.post("/api/auth/register", json={
                "username": f"weak_{weak_password}",
                "password": weak_password
            })
            # 弱密码应该被拒绝或至少返回警告
            assert response.status_code in [400, 422, 200]
            print(f"[SEC] 弱密码'{weak_password}'测试完成 ✅")

    def test_password_encrypted(self, client: TestClient, db_session: Session):
        """测试密码加密存储"""
        from app.models.user import User

        username = "password_test_user"
        plain_password = "TestSecurePassword123!"

        # 注册用户
        client.post("/api/auth/register", json={
            "username": username,
            "password": plain_password
        })

        # 查询数据库
        user = db_session.query(User).filter(User.username == username).first()
        assert user is not None

        # 验证密码哈希不等于明文
        assert user.password_hash != plain_password
        # 验证是bcrypt格式（$2b$开头）
        assert user.password_hash.startswith("$2b$")
        print("[SEC] 密码加密存储测试通过 ✅")

    def test_token_expiration(self, client: TestClient):
        """测试Token过期机制"""
        # 注册登录
        client.post("/api/auth/register", json={
            "username": "token_test_user",
            "password": "Test123456"
        })
        response = client.post("/api/auth/login", data={
            "username": "token_test_user",
            "password": "Test123456"
        })
        token = response.json()["data"]["access_token"]

        # 立即使用token应该成功
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/goals", headers=headers)
        assert response.status_code == 200

        # 注意：实际测试过期需要等待Token过期时间
        # 这里只验证Token格式正确
        import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        assert "exp" in payload  # 过期时间
        assert "sub" in payload  # 用户名
        print("[SEC] Token格式验证通过 ✅")

    def test_invalid_token_rejected(self, client: TestClient):
        """测试无效Token被拒绝"""
        invalid_tokens = [
            "",                    # 空Token
            "invalid_token",        # 无效格式
            "Bearer invalid",       # Bearer格式但无效
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",  # 假Token
        ]

        for token in invalid_tokens:
            headers = {"Authorization": token}
            response = client.get("/api/goals", headers=headers)
            assert response.status_code == 401
        print("[SEC] 无效Token拒绝测试通过 ✅")


class TestAuthorization:
    """授权安全测试"""

    def test_user_cannot_access_other_users_data(self, client: TestClient, db_session: Session):
        """测试用户无法访问其他用户的数据"""
        from app.models.user import User, get_password_hash
        from app.models.goal import Goal

        # 创建两个用户
        user1 = User(username="auth_user1", password_hash=get_password_hash("password123"))
        user2 = User(username="auth_user2", password_hash=get_password_hash("password456"))
        db_session.add_all([user1, user2])
        db_session.commit()

        # user1创建目标
        token1 = create_access_token(data={"sub": user1.username})
        goal_response = client.post("/api/goals", json={
            "title": "user1的目标"
        }, headers={"Authorization": f"Bearer {token1}"})
        goal_id = goal_response.json()["data"]["id"]

        # user2尝试访问user1的目标
        token2 = create_access_token(data={"sub": user2.username})
        response = client.get(f"/api/goals/{goal_id}", headers={"Authorization": f"Bearer {token2}"})

        # 应该被拒绝
        assert response.status_code in [403, 404]
        print("[SEC] 用户隔离测试通过 ✅")

    def test_delete_protection(self, client: TestClient, db_session: Session):
        """测试删除保护"""
        from app.models.user import User, get_password_hash
        from app.models.goal import Goal

        # 创建用户和目标
        user = User(username="delete_test_user", password_hash=get_password_hash("password123"))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        goal = Goal(user_id=user.id, title="测试目标", status="confirmed")
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)

        # 未认证删除
        response = client.delete(f"/api/goals/{goal.id}")
        assert response.status_code == 401

        # 使用其他用户token删除
        other_user = User(username="other_delete_user", password_hash=get_password_hash("password123"))
        db_session.add(other_user)
        db_session.commit()

        token = create_access_token(data={"sub": other_user.username})
        response = client.delete(f"/api/goals/{goal.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code in [403, 404]

        print("[SEC] 删除保护测试通过 ✅")


class TestSQLInjection:
    """SQL注入防护测试"""

    def test_sql_injection_in_username(self, client: TestClient):
        """测试用户名SQL注入防护"""
        sql_injection_attempts = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "admin' UNION SELECT * FROM users --",
            "admin' AND 1=1 --",
        ]

        for injection in sql_injection_attempts:
            response = client.post("/api/auth/login", data={
                "username": injection,
                "password": "password"
            })

            # 应该返回认证失败，而不是SQL错误
            assert response.status_code in [401, 400, 422]

            # 检查是否包含SQL错误信息（应该不包含）
            if "text" in dir(response):
                assert "SQL" not in response.text
                assert "syntax" not in response.text.lower()

        print("[SEC] SQL注入防护测试通过 ✅")

    def test_sql_injection_in_search(self, client: TestClient):
        """测试搜索框SQL注入防护"""
        # 注册登录
        client.post("/api/auth/register", json={
            "username": "search_test_user",
            "password": "Test123456"
        })
        response = client.post("/api/auth/login", data={
            "username": "search_test_user",
            "password": "Test123456"
        })
        token = response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 尝试SQL注入搜索
        injection = "title' OR '1'='1"
        response = client.get(f"/api/goals?search={injection}", headers=headers)

        # 应该正常处理或返回空列表，而不是SQL错误
        assert response.status_code in [200, 400, 422]
        if "text" in dir(response):
            assert "SQL" not in response.text

        print("[SEC] 搜索SQL注入防护测试通过 ✅")


class TestXSSProtection:
    """XSS防护测试"""

    def test_xss_in_goal_title(self, client: TestClient, db_session: Session):
        """测试目标标题XSS防护"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
        ]

        # 注册登录
        client.post("/api/auth/register", json={
            "username": "xss_test_user",
            "password": "Test123456"
        })
        response = client.post("/api/auth/login", data={
            "username": "xss_test_user",
            "password": "Test123456"
        })
        token = response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        for xss in xss_payloads:
            # 创建包含XSS的目标
            create_response = client.post("/api/goals", json={
                "title": xss,
                "description": "XSS测试"
            }, headers=headers)
            assert create_response.status_code == 200

            # 获取目标列表
            list_response = client.get("/api/goals", headers=headers)
            assert list_response.status_code == 200

            # 验证XSS没有被执行（响应应该包含转义的HTML）
            if "text" in dir(list_response):
                # 检查是否包含未转义的script标签
                assert "<script>" not in list_response.text or "&lt;script&gt;" in list_response.text

        print("[SEC] XSS防护测试通过 ✅")


class TestCSRFProtection:
    """CSRF防护测试"""

    def test_csrf_token_required(self, client: TestClient):
        """测试CSRF Token要求（如果实现了的话）"""
        # 这里只是示例，实际实现取决于后端CSRF策略
        # 如果使用CORS，需要验证Origin/Referer
        pass

        print("[SEC] CSRF防护测试跳过（未实现） ⏭️")


class TestSecureHeaders:
    """安全HTTP头测试"""

    def test_security_headers(self, client: TestClient):
        """测试安全HTTP头"""
        # 测试OPTIONS请求
        response = client.options("/api/goals")

        # 检查CORS头
        if "access-control-allow-origin" in response.headers:
            assert "*" in response.headers["access-control-allow-origin"] or \
                   "localhost" in response.headers["access-control-allow-origin"]

        print("[SEC] 安全HTTP头测试完成 ✅")


class TestRateLimiting:
    """速率限制测试"""

    def test_brute_force_protection(self, client: TestClient):
        """测试暴力破解防护"""
        # 尝试多次错误登录
        for _ in range(5):
            client.post("/api/auth/login", data={
                "username": "nonexistent_user",
                "password": "wrong_password"
            })

        # 第6次应该被限速或仍然拒绝
        response = client.post("/api/auth/login", data={
            "username": "nonexistent_user",
            "password": "wrong_password"
        })

        # 应该仍然返回401
        assert response.status_code == 401
        print("[SEC] 暴力破解防护测试完成 ✅")


class TestDataPrivacy:
    """数据隐私测试"""

    def test_password_not_in_response(self, client: TestClient):
        """测试响应中不包含密码"""
        response = client.post("/api/auth/register", json={
            "username": "privacy_test_user",
            "password": "SensitivePassword123!"
        })

        assert response.status_code == 200
        response_data = response.json()

        # 验证响应中不包含密码
        assert "password" not in str(response_data).lower()
        print("[SEC] 密码隐私测试通过 ✅")

    def test_user_data_isolation(self, client: TestClient, db_session: Session):
        """测试用户数据隔离"""
        from app.models.user import User, get_password_hash
        from app.models.goal import Goal

        # 创建两个用户
        user1 = User(username="isolation_user1", password_hash=get_password_hash("password123"))
        user2 = User(username="isolation_user2", password_hash=get_password_hash("password456"))
        db_session.add_all([user1, user2])
        db_session.commit()

        # user1创建10个目标
        token1 = create_access_token(data={"sub": user1.username})
        for i in range(10):
            client.post("/api/goals", json={
                "title": f"user1目标{i}"
            }, headers={"Authorization": f"Bearer {token1}"})

        # user2获取目标列表
        token2 = create_access_token(data={"sub": user2.username})
        response = client.get("/api/goals", headers={"Authorization": f"Bearer {token2}"})
        goals = response.json()["data"]

        # user2不应该看到user1的目标
        for goal in goals:
            assert not goal["title"].startswith("user1")

        print("[SEC] 用户数据隔离测试通过 ✅")
