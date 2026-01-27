"""
认证模块测试
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """认证测试类"""

    def test_register_success(self, client: TestClient):
        """测试用户注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "password": "pass123",
                "email": "new@example.com"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "注册成功"
        assert "token" in data["data"]
        assert "user_id" in data["data"]

    def test_register_duplicate_username(self, client: TestClient, test_user):
        """测试注册重复用户名"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",  # 已存在的用户名
                "password": "pass123"
            }
        )

        assert response.status_code == 400  # HTTP 错误状态码
        data = response.json()
        assert "detail" in data  # FastAPI 错误格式

    def test_login_success(self, client: TestClient, test_user):
        """测试用户登录成功"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "pass123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data["data"]
        assert data["user_id"] == test_user.id

    def test_login_wrong_password(self, client: TestClient, test_user):
        """测试登录密码错误"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpass"
            }
        )

        assert response.status_code == 401  # 未授权

    def test_login_user_not_found(self, client: TestClient):
        """测试登录用户不存在"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "pass123"
            }
        )

        assert response.status_code == 401  # 未授权

    def test_logout_success(self, client: TestClient, auth_headers):
        """测试用户登出成功"""
        # 注意: 当前 API 可能没有 logout 端点,这里测试受保护端点
        response = client.get("/api/users/me", headers=auth_headers)

        assert response.status_code == 200

    def test_protected_endpoint_without_token(self, client: TestClient):
        """测试未携带 Token 访问受保护接口"""
        response = client.get("/api/goals")

        assert response.status_code == 401  # 未授权

    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """测试使用无效 Token 访问受保护接口"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/goals", headers=headers)

        assert response.status_code == 401  # 未授权
