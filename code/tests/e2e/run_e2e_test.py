"""
E2E测试执行脚本
用于测试前后端联调
"""
import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# 注释掉有问题的导入，因为这个文件主要用于手动运行
# from tests.e2e.agent.test_runner import E2ETestRunner, TestStep, TestScenario


async def test_simple_request():
    """简单的HTTP请求测试"""
    print("=== 简单E2E测试 ===\n")

    # 注意：此测试需要前端测试页面已启动并连接到WebSocket
    # 实际使用时，需要：
    # 1. 启动后端服务
    # 2. 启动前端（HBuilderX或CLI）
    # 3. 打开测试页面 /pages/test/simple-e2e-test
    # 4. 运行此脚本

    print("说明：")
    print("1. 启动后端服务: cd backend && python main.py")
    print("2. 启动前端: 在HBuilderX中运行到浏览器")
    print("3. 访问测试页面: http://localhost:8080/#/pages/test/simple-e2e-test")
    print("4. 测试页面会连接到 ws://localhost:8765")
    print("5. 运行此脚本进行测试\n")

    print("当前仅执行后端API测试，前端测试需要手动执行")
    return None


async def test_frontend_api_communication():
    """测试前端与后端API通信"""
    print("\n=== 测试前后端通信 ===\n")

    # 使用requests直接测试后端API
    import requests

    base_url = "http://localhost:8000"

    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")

    print("\n2. 测试注册接口...")
    try:
        import random
        username = f"test_user_{random.randint(1000, 9999)}"
        response = requests.post(
            f"{base_url}/api/auth/register",
            json={
                "username": username,
                "password": "TestPass123",
                "email": f"{username}@test.com"
            },
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")

        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("token")

            if token:
                print(f"\n3. 测试登录接口...")
                response = requests.post(
                    f"{base_url}/api/auth/login",
                    json={
                        "username": username,
                        "password": "TestPass123"
                    },
                    timeout=5
                )
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")


def main():
    """主函数"""
    print("LifeManager E2E测试工具\n")

    # 检查后端是否运行
    import requests
    try:
        requests.get("http://localhost:8000/health", timeout=2)
        print("✓ 后端服务运行正常\n")
    except:
        print("✗ 后端服务未启动！")
        print("请先启动后端: cd backend && python main.py\n")
        return

    # 运行测试
    asyncio.run(test_simple_request())
    asyncio.run(test_frontend_api_communication())

    print("\n=== 测试完成 ===")
    print("\n提示：")
    print("- 集成测试: pytest tests/integration/ -v")
    print("- 数据库测试: pytest tests/integration/test_database.py -v")
    print("- 完整集成测试: pytest tests/integration/ -v")


if __name__ == "__main__":
    main()
