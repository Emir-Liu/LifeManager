"""
测试聊天服务功能
"""
import pytest
from app.services.chat_service import ChatService


def test_chat_service_initialization():
    """测试聊天服务初始化"""
    service = ChatService()
    assert service is not None


def test_chat_fallback_response():
    """测试降级响应"""
    service = ChatService()
    
    # 测试问候
    response = service._get_fallback_response("你好")
    assert response is not None
    assert len(response) > 0
    
    # 测试目标相关
    response = service._get_fallback_response("如何制定目标")
    assert "SMART" in response or "目标" in response
    
    # 测试任务相关
    response = service._get_fallback_response("怎么管理任务")
    assert "任务" in response
    
    # 测试普通问题
    response = service._get_fallback_response("你好吗？")
    assert response is not None


def test_chat_with_fallback():
    """测试完整聊天流程（降级模式）"""
    service = ChatService()
    
    # 强制使用降级模式
    service.llm_operator = None
    
    response = service.chat("你好", None)
    assert response is not None
    assert len(response) > 0


if __name__ == "__main__":
    # 运行简单测试
    service = ChatService()
    
    print("测试降级回复:")
    test_messages = [
        "你好",
        "如何制定目标",
        "怎么管理任务",
        "提高效率的方法",
        "谢谢"
    ]
    
    for msg in test_messages:
        print(f"\n用户: {msg}")
        print(f"助手: {service._get_fallback_response(msg)}")
