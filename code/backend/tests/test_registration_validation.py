"""
注册接口异常测试
测试各种异常情况：邮箱重复、格式错误、密码不一致、用户名不合格等
"""
import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash


class TestRegistrationValidation:
    """注册验证测试"""
    
    def test_register_success(self, client, db: Session):
        """测试正常注册"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "password": "password123",
                "email": "newuser@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "注册成功"
        assert "user_id" in data["data"]
        assert "token" in data["data"]
    
    def test_register_duplicate_username(self, client, db: Session):
        """测试用户名重复"""
        # 创建已存在的用户
        existing_user = User(
            username="existing_user",
            password_hash=get_password_hash("password123"),
            email="existing@example.com"
        )
        db.add(existing_user)
        db.commit()
        
        # 尝试用相同用户名注册
        response = client.post(
            "/api/auth/register",
            json={
                "username": "existing_user",
                "password": "password123",
                "email": "another@example.com"
            }
        )
        # 现在返回200，但code=400表示错误
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400
        assert data["message"] == "注册失败"
        assert "该用户名已注册" in data["data"]["reason"]
        
        # 清理
        db.query(User).filter(User.username == "existing_user").delete()
        db.commit()
    
    def test_register_duplicate_email(self, client, db: Session):
        """测试邮箱重复"""
        # 创建已存在的用户
        existing_user = User(
            username="existing_email_user",
            password_hash=get_password_hash("password123"),
            email="existing@example.com"
        )
        db.add(existing_user)
        db.commit()
        
        # 尝试用相同邮箱注册
        response = client.post(
            "/api/auth/register",
            json={
                "username": "new_user",
                "password": "password123",
                "email": "existing@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400
        assert data["message"] == "注册失败"
        assert "该邮箱已注册" in data["data"]["reason"]
        
        # 清理
        db.query(User).filter(User.username == "existing_email_user").delete()
        db.commit()
    
    def test_register_username_too_short(self, client):
        """测试用户名过短"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "ab",  # 少于3个字符
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_register_username_too_long(self, client):
        """测试用户名过长"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "a" * 51,  # 超过50个字符
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_username_empty(self, client):
        """测试用户名为空"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "",
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_username_missing(self, client):
        """测试缺少用户名"""
        response = client.post(
            "/api/auth/register",
            json={
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_password_too_short(self):
        """测试密码过短"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "12345",  # 少于6个字符
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_password_too_long(self):
        """测试密码过长"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "a" * 51,  # 超过50个字符
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_password_empty(self):
        """测试密码为空"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_password_missing(self):
        """测试缺少密码"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_invalid_email_format(self):
        """测试邮箱格式错误"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123",
                "email": "invalid-email"  # 无效的邮箱格式
            }
        )
        assert response.status_code == 422
    
    def test_register_invalid_email_format2(self):
        """测试邮箱格式错误（缺少@）"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123",
                "email": "invalidemail.com"
            }
        )
        assert response.status_code == 422
    
    def test_register_invalid_email_format3(self):
        """测试邮箱格式错误（缺少域名）"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "password": "password123",
                "email": "test@"
            }
        )
        assert response.status_code == 422
    
    def test_register_without_email(self):
        """测试不提供邮箱（邮箱是可选的）"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser_no_email",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "注册成功"
    
    def test_register_username_with_special_chars(self):
        """测试用户名包含特殊字符"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "user@name",  # 包含@符号
                "password": "password123",
                "email": "test@example.com"
            }
        )
        # FastAPI/Pydantic 默认允许特殊字符
        assert response.status_code == 200
    
    def test_register_username_with_spaces(self):
        """测试用户名包含空格"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "user name",  # 包含空格
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
    
    def test_register_username_with_chinese(self):
        """测试用户名为中文"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "测试用户",
                "password": "password123",
                "email": "test@example.com"
            }
        )
        # Unicode字符应该被支持
        assert response.status_code == 200
    
    def test_register_with_null_email(self):
        """测试邮箱为null"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser_null",
                "password": "password123",
                "email": None
            }
        )
        assert response.status_code == 200
    
    def test_register_with_empty_string_email(self):
        """测试邮箱为空字符串"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser_empty",
                "password": "password123",
                "email": ""
            }
        )
        # 空字符串邮箱应该是无效的
        assert response.status_code == 422
    
    def test_register_malformed_json(self):
        """测试JSON格式错误"""
        response = client.post(
            "/api/auth/register",
            content="invalid json"
        )
        assert response.status_code == 422


class TestRegistrationEdgeCases:
    """注册边界情况测试"""
    
    def test_register_min_length_username(self, db: Session):
        """测试最小长度用户名（3个字符）"""
        # 清理
        db.query(User).filter(User.username == "abc").delete()
        db.commit()
        
        response = client.post(
            "/api/auth/register",
            json={
                "username": "abc",
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
    
    def test_register_max_length_username(self, db: Session):
        """测试最大长度用户名（50个字符）"""
        username = "a" * 50
        # 清理
        db.query(User).filter(User.username == username).delete()
        db.commit()
        
        response = client.post(
            "/api/auth/register",
            json={
                "username": username,
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
    
    def test_register_min_length_password(self, db: Session):
        """测试最小长度密码（6个字符）"""
        # 清理
        db.query(User).filter(User.username == "testuser_min_pwd").delete()
        db.commit()
        
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser_min_pwd",
                "password": "123456",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
    
    def test_register_max_length_password(self, db: Session):
        """测试最大长度密码（50个字符）"""
        password = "a" * 50
        # 清理
        db.query(User).filter(User.username == "testuser_max_pwd").delete()
        db.commit()
        
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser_max_pwd",
                "password": password,
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200


class TestRegistrationResponseData:
    """注册响应数据测试"""
    
    def test_register_response_structure(self, db: Session):
        """测试注册响应数据结构"""
        # 清理
        db.query(User).filter(User.username == "testuser_structure").delete()
        db.commit()
        
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser_structure",
                "password": "password123",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # 验证响应结构
        assert "code" in data
        assert "message" in data
        assert "data" in data
        
        # 验证数据结构
        assert "user_id" in data["data"]
        assert "username" in data["data"]
        assert "token" in data["data"]
        assert "refresh_token" in data["data"]
        
        # 验证数据类型
        assert isinstance(data["code"], int)
        assert isinstance(data["message"], str)
        assert isinstance(data["data"]["user_id"], int)
        assert isinstance(data["data"]["username"], str)
        assert isinstance(data["data"]["token"], str)
        assert isinstance(data["data"]["refresh_token"], str)
    
    def test_register_token_not_empty(self, db: Session):
        """测试返回的token不为空"""
        # 清理
        db.query(User).filter(User.username == "testuser_token").delete()
        db.commit()
        
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser_token",
                "password": "password123",
                "email": "test@example.com"
            }
        )
        data = response.json()
        
        assert len(data["data"]["token"]) > 0
        assert len(data["data"]["refresh_token"]) > 0
    
    def test_register_returned_username_matches(self, db: Session):
        """测试返回的用户名与注册时一致"""
        username = "testuser_match"
        # 清理
        db.query(User).filter(User.username == username).delete()
        db.commit()
        
        response = client.post(
            "/api/auth/register",
            json={
                "username": username,
                "password": "password123",
                "email": "test@example.com"
            }
        )
        data = response.json()
        
        assert data["data"]["username"] == username
