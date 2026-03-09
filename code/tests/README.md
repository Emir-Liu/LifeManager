# LifeManager E2E 测试文档

## 概述

本文档描述 LifeManager 项目的前后端联调 E2E 测试框架，用于验证前端 Uni-app 与后端 FastAPI 的完整交互流程。

## 测试架构

```
┌─────────────────────────────────────────────────────────────┐
│                      智能体测试驱动                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  test_runner.py - 测试执行器                          │  │
│  │  request_interceptor.py - 请求拦截器                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                    前端测试页面                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  e2e-test.vue - 测试控制器                            │  │
│  │  ├─ 嵌入真实业务页面（注册/登录等）                    │  │
│  │  ├─ 拦截 uni.request 请求                             │  │
│  │  └─ 执行智能体指令并上报结果                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP API
┌─────────────────────────▼───────────────────────────────────┐
│                      后端服务                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FastAPI + SQLite/PostgreSQL                          │  │
│  │  ├─ 认证 API                                          │  │
│  │  ├─ 目标管理 API                                      │  │
│  │  └─ 任务管理 API                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
tests/
├── integration/          # 集成测试（纯后端API测试）
│   ├── __init__.py
│   ├── conftest.py       # pytest配置
│   ├── test_api_flow.py  # API流程测试
│   └── test_database.py  # 数据库集成测试
├── e2e/                  # 端到端测试（前后端联调）
│   ├── frontend/         # 前端测试页面
│   │   └── pages/
│   │       └── test/
│   │           └── e2e-test.vue
│   └── agent/            # 智能体测试驱动
│       ├── __init__.py
│       ├── test_runner.py
│       └── request_interceptor.py
├── data/
│   └── test_scenarios.json
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
# 后端测试依赖
cd backend
pip install -r requirements.txt
pip install websockets pytest-asyncio
```

### 2. 启动服务

**终端1 - 启动后端服务：**
```bash
cd backend
python main.py
# 服务将在 http://localhost:8000 启动
```

**终端2 - 启动前端（HBuilderX或CLI）：**
```bash
cd frontend
# HBuilderX: 运行到浏览器或模拟器
# 或
npm run dev:h5
```

### 3. 运行集成测试

```bash
cd tests/integration
pytest -v
```

### 4. 配置前端测试页面

在 `frontend/pages.json` 中添加测试页面路径：

```json
{
  "pages": [
    {
      "path": "pages/test/e2e-test",
      "style": {
        "navigationBarTitleText": "E2E测试"
      }
    }
  ]
}
```

将 `tests/e2e/frontend/pages/test/e2e-test.vue` 复制到 `frontend/pages/test/` 目录。

### 5. 启动 WebSocket 服务器（用于智能体通信）

```bash
# 创建 ws_server.py
python tests/e2e/agent/ws_server.py
```

## 使用指南

### 编写E2E测试用例

#### 方法1：使用Python代码

```python
import asyncio
from tests.e2e.agent.test_runner import E2ETestRunner, TestScenario, TestStep

async def test_register():
    runner = E2ETestRunner()
    await runner.connect()

    # 定义测试场景
    scenario = TestScenario(
        name="用户注册",
        description="测试用户注册流程",
        steps=[
            TestStep(
                name="加载注册页面",
                action="load_page",
                params={"page": "register"},
                wait_after=500
            ),
            TestStep(
                name="填写表单",
                action="fill_form",
                params={
                    "data": {
                        "username": "newuser",
                        "email": "new@example.com",
                        "password": "pass123",
                        "confirmPassword": "pass123"
                    }
                }
            ),
            TestStep(
                name="点击注册",
                action="click",
                params={"action": "register"},
                wait_after=2000
            )
        ]
    )

    # 执行测试
    result = await runner.execute_scenario(scenario)
    print(f"测试结果: {'通过' if result.passed else '失败'}")

    # 验证数据库状态
    db_checks = runner.verify_database_state({
        "user_exists": {"username": "newuser"}
    })
    print(f"数据库验证: {db_checks}")

    await runner.disconnect()

# 运行
asyncio.run(test_register())
```

### 支持的指令

| 指令 | 描述 | 参数 |
|------|------|------|
| `load_page` | 加载页面 | `page`: register/login |
| `fill_form` | 填充表单 | `field`, `value` 或 `data` |
| `click_element` | 点击元素 | `action`, `selector` |
| `verify_element` | 验证元素 | `selector`, `expected` |
| `get_request_history` | 获取请求历史 | - |
| `clear_storage` | 清除本地存储 | - |
| `execute_scenario` | 执行场景 | `scenario` |

## 测试场景示例

### 场景1：用户注册成功

```python
from tests.e2e.agent.test_runner import TestScenarios

scenario = TestScenarios.register_success_scenario()
```

**测试步骤：**
1. 加载注册页面
2. 填写用户名、邮箱、密码
3. 点击注册按钮
4. 验证注册请求发送成功
5. 验证响应状态码为200
6. 验证数据库中用户已创建

## 故障排查

### 常见问题

**Q: WebSocket连接失败**
- 检查前端页面是否已加载
- 确认WebSocket服务器地址正确
- 检查防火墙设置

**Q: 请求未被拦截**
- 确认 `e2e-test.vue` 已正确加载
- 检查 `uni.request` 是否被正确重写
- 查看浏览器控制台是否有错误

**Q: 数据库验证失败**
- 确认后端使用的是测试数据库
- 检查数据库连接字符串
- 验证测试数据是否正确写入
