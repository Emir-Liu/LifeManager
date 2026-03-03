"""测试 Conversation API
测试对话相关的 API 端点
"""
import pytest


class TestConversationAPI:
    """对话API测试"""

    def test_create_conversation_success(self, client, auth_headers: dict):
        """测试成功创建对话"""
        response = client.post(
            "/api/conversations",
            json={
                "title": "测试对话",
                "conversation_type": "goal_planning"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "success"
        assert "data" in data
        assert "id" in data["data"]
        assert data["data"]["title"] == "测试对话"

    def test_create_conversation_unauthorized(self, client):
        """测试未授权创建对话"""
        response = client.post(
            "/api/conversations",
            json={
                "title": "测试对话",
                "conversation_type": "goal_planning"
            }
        )

        assert response.status_code == 401

    def test_get_conversations_list(self, client, auth_headers: dict):
        """测试获取对话列表"""
        # 先创建一个对话
        client.post(
            "/api/conversations",
            json={"title": "列表测试", "conversation_type": "goal_planning"},
            headers=auth_headers
        )

        response = client.get(
            "/api/conversations",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)

    def test_get_conversation_by_id(self, client, auth_headers: dict):
        """测试获取单个对话详情"""
        # 创建对话
        create_resp = client.post(
            "/api/conversations",
            json={"title": "详情测试", "conversation_type": "goal_planning"},
            headers=auth_headers
        )
        conversation_id = create_resp.json()["data"]["id"]

        response = client.get(
            f"/api/conversations/{conversation_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == conversation_id

    def test_update_conversation(self, client, auth_headers: dict):
        """测试更新对话"""
        # 创建对话
        create_resp = client.post(
            "/api/conversations",
            json={"title": "更新前", "conversation_type": "goal_planning"},
            headers=auth_headers
        )
        conversation_id = create_resp.json()["data"]["id"]

        response = client.put(
            f"/api/conversations/{conversation_id}",
            json={"title": "更新后"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "更新后"

    def test_delete_conversation(self, client, auth_headers: dict):
        """测试删除对话"""
        # 创建对话
        create_resp = client.post(
            "/api/conversations",
            json={"title": "删除测试", "conversation_type": "goal_planning"},
            headers=auth_headers
        )
        conversation_id = create_resp.json()["data"]["id"]

        response = client.delete(
            f"/api/conversations/{conversation_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_send_message(self, client, auth_headers: dict):
        """测试发送消息"""
        # 创建对话
        create_resp = client.post(
            "/api/conversations",
            json={"title": "消息测试", "conversation_type": "general_chat"},
            headers=auth_headers
        )
        conversation_id = create_resp.json()["data"]["id"]

        response = client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"content": "你好，AI助手！", "role": "user"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert data["data"]["content"] == "你好，AI助手！"

    def test_get_messages(self, client, auth_headers: dict):
        """测试获取消息列表"""
        # 创建对话并发送消息
        create_resp = client.post(
            "/api/conversations",
            json={"title": "消息列表测试", "conversation_type": "general_chat"},
            headers=auth_headers
        )
        conversation_id = create_resp.json()["data"]["id"]

        client.post(
            f"/api/conversations/{conversation_id}/messages",
            json={"content": "第一条消息", "role": "user"},
            headers=auth_headers
        )

        response = client.get(
            f"/api/conversations/{conversation_id}/messages",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) > 0

    def test_conversation_not_found(self, client, auth_headers: dict):
        """测试访问不存在的对话"""
        response = client.get(
            "/api/conversations/99999",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404
        assert "not found" in data["message"].lower()

    def test_send_message_to_nonexistent_conversation(self, client, auth_headers: dict):
        """测试向不存在的对话发送消息"""
        response = client.post(
            "/api/conversations/99999/messages",
            json={"content": "测试消息", "role": "user"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404
