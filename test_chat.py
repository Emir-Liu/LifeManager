"""
简单的聊天服务测试脚本
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 设置环境变量
os.environ.setdefault('LLM_MODEL_API_KEY', '')

from app.services.chat_service import chat_service

def test_chat():
    """测试聊天功能"""
    print("=" * 60)
    print("聊天服务测试")
    print("=" * 60)
    
    # 测试消息列表
    test_messages = [
        "你好",
        "如何制定目标？",
        "怎么管理任务？",
        "谢谢"
    ]
    
    for msg in test_messages:
        print(f"\n👤 用户: {msg}")
        try:
            response = chat_service.chat(msg, [])
            print(f"🤖 助手: {response}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_chat()
