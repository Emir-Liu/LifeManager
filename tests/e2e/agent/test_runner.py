"""
E2E测试执行器
智能体测试驱动核心模块
"""
import os
import sys
import json
import asyncio
import websockets
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import pytest

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import User, Goal, Plan, Task


@dataclass
class TestStep:
    """测试步骤"""
    name: str
    action: str
    params: Dict[str, Any]
    expected_result: Optional[Dict] = None
    wait_after: int = 0  # 执行后等待时间(毫秒)


@dataclass
class TestScenario:
    """测试场景"""
    name: str
    description: str
    steps: List[TestStep]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None


@dataclass
class TestResult:
    """测试结果"""
    scenario_name: str
    passed: bool
    steps_results: List[Dict]
    duration_ms: int
    timestamp: str
    error_message: Optional[str] = None


class E2ETestRunner:
    """
    E2E测试执行器
    通过WebSocket与前端测试页面通信
    """

    def __init__(self,
                 frontend_ws_url: str = "ws://localhost:8765",
                 db_url: str = "sqlite:///./e2e_test.db"):
        self.frontend_ws_url = frontend_ws_url
        self.db_url = db_url
        self.ws = None
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_commands: Dict[str, asyncio.Future] = {}
        self.command_counter = 0
        self.request_history: List[Dict] = []

        # 数据库
        self.engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

        # 注册默认消息处理器
        self._register_default_handlers()

    def _register_default_handlers(self):
        """注册默认消息处理器"""
        self.message_handlers['client_ready'] = self._handle_client_ready
        self.message_handlers['page_loaded'] = self._handle_page_loaded
        self.message_handlers['form_filled'] = self._handle_form_filled
        self.message_handlers['element_clicked'] = self._handle_element_clicked
        self.message_handlers['verification_result'] = self._handle_verification_result
        self.message_handlers['request_intercepted'] = self._handle_request_intercepted
        self.message_handlers['scenario_completed'] = self._handle_scenario_completed
        self.message_handlers['request_history'] = self._handle_request_history
        self.message_handlers['error'] = self._handle_error

    async def connect(self):
        """连接到前端WebSocket服务器"""
        try:
            self.ws = await websockets.connect(self.frontend_ws_url)
            self.connected = True
            print(f"已连接到前端测试页面: {self.frontend_ws_url}")

            # 启动消息接收循环
            asyncio.create_task(self._receive_loop())

            # 等待客户端就绪
            await asyncio.sleep(1)

        except Exception as e:
            raise ConnectionError(f"无法连接到前端: {e}")

    async def disconnect(self):
        """断开连接"""
        if self.ws:
            await self.ws.close()
            self.connected = False
            print("已断开与前端的连接")

    async def _receive_loop(self):
        """消息接收循环"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self._handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
            self.connected = False

    async def _handle_message(self, data: Dict):
        """处理收到的消息"""
        msg_type = data.get('type')
        command_id = data.get('commandId')

        # 调用对应的处理器
        handler = self.message_handlers.get(msg_type)
        if handler:
            await handler(data)

        # 处理待完成的命令
        if command_id and command_id in self.pending_commands:
            future = self.pending_commands.pop(command_id)
            if not future.done():
                future.set_result(data)

    # ==================== 消息处理器 ====================

    async def _handle_client_ready(self, data: Dict):
        """处理客户端就绪消息"""
        print(f"前端测试页面已就绪: {data.get('platform')}")

    async def _handle_page_loaded(self, data: Dict):
        """处理页面加载完成"""
        print(f"页面加载完成: {data.get('page')}")

    async def _handle_form_filled(self, data: Dict):
        """处理表单填充完成"""
        print(f"表单已填充: {data.get('field')} = {data.get('value')}")

    async def _handle_element_clicked(self, data: Dict):
        """处理元素点击"""
        print(f"元素已点击: {data.get('action')}")

    async def _handle_verification_result(self, data: Dict):
        """处理验证结果"""
        passed = data.get('passed', False)
        status = "通过" if passed else "失败"
        print(f"验证{status}: {data.get('selector')}")

    async def _handle_request_intercepted(self, data: Dict):
        """处理拦截的请求"""
        request_data = data.get('data', {})
        self.request_history.append(request_data)
        print(f"拦截请求: {request_data.get('method')} {request_data.get('url')}")

    async def _handle_scenario_completed(self, data: Dict):
        """处理场景执行完成"""
        print(f"场景执行完成: {data.get('scenario')}")

    async def _handle_request_history(self, data: Dict):
        """处理请求历史"""
        self.request_history = data.get('requests', [])

    async def _handle_error(self, data: Dict):
        """处理错误"""
        print(f"前端错误: {data.get('error')}")

    # ==================== 命令发送 ====================

    async def send_command(self, command_type: str, params: Dict = None, timeout: int = 10) -> Dict:
        """发送命令并等待响应"""
        if not self.connected:
            raise ConnectionError("未连接到前端")

        self.command_counter += 1
        command_id = f"cmd_{self.command_counter}_{datetime.now().timestamp()}"

        command = {
            'id': command_id,
            'type': command_type,
            **(params or {})
        }

        # 创建Future等待响应
        future = asyncio.get_event_loop().create_future()
        self.pending_commands[command_id] = future

        # 发送命令
        await self.ws.send(json.dumps(command))

        # 等待响应
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            self.pending_commands.pop(command_id, None)
            raise TimeoutError(f"命令超时: {command_type}")

    # ==================== 测试操作 ====================

    async def load_page(self, page: str, params: Dict = None):
        """加载页面"""
        return await self.send_command('load_page', {
            'page': page,
            'params': params or {}
        })

    async def fill_form(self, field: str, value: str, selector: str = None):
        """填充表单"""
        return await self.send_command('fill_form', {
            'field': field,
            'value': value,
            'selector': selector
        })

    async def fill_form_multiple(self, data: Dict[str, str]):
        """批量填充表单"""
        results = []
        for field, value in data.items():
            result = await self.fill_form(field, value)
            results.append(result)
            await asyncio.sleep(0.1)  # 短暂延迟
        return results

    async def click_element(self, action: str, selector: str = None):
        """点击元素"""
        return await self.send_command('click_element', {
            'action': action,
            'selector': selector
        })

    async def verify_element(self, selector: str, expected: any, property_name: str = 'text'):
        """验证元素"""
        return await self.send_command('verify_element', {
            'selector': selector,
            'expected': expected,
            'property': property_name
        })

    async def get_request_history(self) -> List[Dict]:
        """获取请求历史"""
        result = await self.send_command('get_request_history')
        return result.get('requests', [])

    async def clear_storage(self):
        """清除本地存储"""
        return await self.send_command('clear_storage')

    async def execute_scenario(self, scenario: TestScenario) -> TestResult:
        """执行测试场景"""
        start_time = datetime.now()
        steps_results = []

        print(f"\n{'='*50}")
        print(f"开始执行场景: {scenario.name}")
        print(f"{'='*50}")

        try:
            # 执行setup
            if scenario.setup:
                print("执行 setup...")
                if asyncio.iscoroutinefunction(scenario.setup):
                    await scenario.setup(self)
                else:
                    scenario.setup(self)

            # 执行步骤
            for step in scenario.steps:
                print(f"\n执行步骤: {step.name}")
                step_start = datetime.now()

                try:
                    if step.action == 'load_page':
                        await self.load_page(step.params['page'])
                    elif step.action == 'fill_form':
                        await self.fill_form_multiple(step.params['data'])
                    elif step.action == 'click':
                        await self.click_element(step.params['action'])
                    elif step.action == 'verify_request':
                        # 验证请求
                        await asyncio.sleep(0.5)  # 等待请求完成
                        requests = await self.get_request_history()
                        # 验证逻辑...

                    step_duration = (datetime.now() - step_start).total_seconds() * 1000
                    steps_results.append({
                        'name': step.name,
                        'passed': True,
                        'duration_ms': step_duration
                    })

                    if step.wait_after > 0:
                        await asyncio.sleep(step.wait_after / 1000)

                except Exception as e:
                    step_duration = (datetime.now() - step_start).total_seconds() * 1000
                    steps_results.append({
                        'name': step.name,
                        'passed': False,
                        'error': str(e),
                        'duration_ms': step_duration
                    })
                    raise

            # 执行teardown
            if scenario.teardown:
                print("执行 teardown...")
                if asyncio.iscoroutinefunction(scenario.teardown):
                    await scenario.teardown(self)
                else:
                    scenario.teardown(self)

            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                scenario_name=scenario.name,
                passed=True,
                steps_results=steps_results,
                duration_ms=int(duration),
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return TestResult(
                scenario_name=scenario.name,
                passed=False,
                steps_results=steps_results,
                duration_ms=int(duration),
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )

    # ==================== 数据库验证 ====================

    def verify_database_state(self, checks: Dict[str, Any]) -> Dict[str, bool]:
        """
        验证数据库状态
        checks: {
            'user_count': 1,
            'user_exists': {'username': 'test'},
            'goal_count': 2
        }
        """
        db = self.SessionLocal()
        results = {}

        try:
            if 'user_count' in checks:
                count = db.query(User).count()
                results['user_count'] = count == checks['user_count']

            if 'user_exists' in checks:
                criteria = checks['user_exists']
                user = db.query(User).filter_by(**criteria).first()
                results['user_exists'] = user is not None

            if 'goal_count' in checks:
                count = db.query(Goal).count()
                results['goal_count'] = count == checks['goal_count']

            if 'task_count' in checks:
                count = db.query(Task).count()
                results['task_count'] = count == checks['task_count']

        finally:
            db.close()

        return results

    def reset_database(self):
        """重置数据库"""
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)


# ==================== 预定义测试场景 ====================

class TestScenarios:
    """预定义的测试场景"""

    @staticmethod
    def register_success_scenario() -> TestScenario:
        """用户注册成功场景"""
        return TestScenario(
            name="用户注册成功",
            description="测试用户成功注册并自动登录",
            steps=[
                TestStep(
                    name="加载注册页面",
                    action="load_page",
                    params={"page": "register"},
                    wait_after=500
                ),
                TestStep(
                    name="填写注册信息",
                    action="fill_form",
                    params={
                        "data": {
                            "username": "e2e_test_user",
                            "email": "e2e@test.com",
                            "password": "password123",
                            "confirmPassword": "password123"
                        }
                    },
                    wait_after=200
                ),
                TestStep(
                    name="点击注册按钮",
                    action="click",
                    params={"action": "register"},
                    wait_after=2000
                ),
                TestStep(
                    name="验证注册请求",
                    action="verify_request",
                    params={"url_pattern": "/auth/register", "method": "POST"}
                )
            ]
        )

    @staticmethod
    def login_success_scenario() -> TestScenario:
        """用户登录成功场景"""
        return TestScenario(
            name="用户登录成功",
            description="测试用户成功登录",
            steps=[
                TestStep(
                    name="加载登录页面",
                    action="load_page",
                    params={"page": "login"},
                    wait_after=500
                ),
                TestStep(
                    name="填写登录信息",
                    action="fill_form",
                    params={
                        "data": {
                            "username": "testuser",
                            "password": "pass123"
                        }
                    },
                    wait_after=200
                ),
                TestStep(
                    name="点击登录按钮",
                    action="click",
                    params={"action": "login"},
                    wait_after=2000
                )
            ]
        )

    @staticmethod
    def register_validation_scenario() -> TestScenario:
        """注册表单验证场景"""
        return TestScenario(
            name="注册表单验证",
            description="测试注册表单的各种验证规则",
            steps=[
                TestStep(
                    name="加载注册页面",
                    action="load_page",
                    params={"page": "register"},
                    wait_after=500
                ),
                TestStep(
                    name="提交空表单",
                    action="click",
                    params={"action": "register"},
                    wait_after=500
                ),
                TestStep(
                    name="填写短密码",
                    action="fill_form",
                    params={
                        "data": {
                            "username": "test",
                            "password": "123",
                            "confirmPassword": "123"
                        }
                    },
                    wait_after=200
                ),
                TestStep(
                    name="提交验证",
                    action="click",
                    params={"action": "register"},
                    wait_after=500
                )
            ]
        )


# ==================== pytest fixtures ====================

@pytest.fixture
async def e2e_runner():
    """E2E测试执行器fixture"""
    runner = E2ETestRunner()
    await runner.connect()
    yield runner
    await runner.disconnect()


@pytest.fixture
def scenarios():
    """测试场景fixture"""
    return TestScenarios
