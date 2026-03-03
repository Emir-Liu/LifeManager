# 测试脚本说明文档

## 目录结构

```
backend/tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # Pytest配置和Fixtures
├── test_auth.py                   # 认证API测试
├── test_goals.py                  # 目标API测试
├── test_plans.py                  # 规划API测试
├── test_tasks.py                  # 任务API测试
├── test_ai_service.py             # AI服务测试
├── test_conflict_service.py       # 冲突检测服务测试
├── test_schedule_service.py       # 时间分配服务测试
├── test_conversation_api.py       # 对话API测试
├── test_event_api.py              # 日程API测试
├── test_time_preference_api.py    # 时间偏好API测试
├── test_timeline_api.py           # 时间线API测试
├── test_integration_phase2.py    # Phase 2 集成测试
└── run_tests.py                   # 测试运行脚本
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. 配置测试环境

测试环境变量在 `conftest.py` 中已配置,使用 `./test.db` 作为测试数据库。

### 3. 运行所有测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并显示输出
pytest tests/ -v -s

# 运行测试并生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### 4. 运行特定测试

```bash
# 运行特定测试文件
pytest tests/test_conversation_api.py -v

# 运行特定测试类
pytest tests/test_conflict_service.py::TestConflictService -v

# 运行特定测试方法
pytest tests/test_conflict_service.py::TestConflictService::test_time_overlap_true -v

# 运行Phase 2相关测试
pytest tests/test_conversation_api.py tests/test_event_api.py tests/test_timeline_api.py -v
```

## 测试分类

### 1. 单元测试

测试单个函数或方法的正确性。

**文件列表:**
- `test_conflict_service.py` - 冲突检测服务单元测试
- `test_schedule_service.py` - 时间分配服务单元测试
- `test_ai_service.py` - AI服务单元测试

**运行:**
```bash
pytest tests/test_conflict_service.py -v
pytest tests/test_schedule_service.py -v
```

### 2. API集成测试

测试API端点的完整请求-响应流程。

**文件列表:**
- `test_auth.py` - 认证API测试
- `test_goals.py` - 目标API测试
- `test_plans.py` - 规划API测试
- `test_tasks.py` - 任务API测试
- `test_conversation_api.py` - 对话API测试
- `test_event_api.py` - 日程API测试
- `test_time_preference_api.py` - 时间偏好API测试
- `test_timeline_api.py` - 时间线API测试

**运行:**
```bash
# 运行所有API测试
pytest tests/test_*_api.py -v

# 运行特定API测试
pytest tests/test_conversation_api.py -v
```

### 3. 集成测试

测试完整业务流程和多模块交互。

**文件列表:**
- `test_integration_phase2.py` - Phase 2 完整业务流程测试

**运行:**
```bash
pytest tests/test_integration_phase2.py -v
```

## 测试覆盖范围

### Phase 2 功能测试

#### 对话层
- ✅ 创建对话会话
- ✅ 获取对话列表
- ✅ 发送消息
- ✅ 获取消息列表
- ✅ 更新对话
- ✅ 删除对话

#### 日程管理
- ✅ 创建日程
- ✅ 获取日程列表
- ✅ 按日期/范围查询
- ✅ 更新日程
- ✅ 删除日程

#### 时间偏好
- ✅ 创建时间偏好
- ✅ 获取时间偏好
- ✅ 更新时间偏好
- ✅ 获取时间统计

#### 时间线
- ✅ 获取时间线
- ✅ 建议任务时间
- ✅ 自动分配任务

#### 冲突检测
- ✅ 任务时间重叠检测
- ✅ 日程重叠检测
- ✅ 解决建议生成

#### 智能时间分配
- ✅ 生成可用时间段
- ✅ 考虑时间偏好
- ✅ 考虑已有日程
- ✅ 自动分配任务时间

## Fixtures 说明

### `db`
创建测试数据库会话,每个测试函数开始前重置数据库。

```python
def test_example(db):
    # db 是一个 SQLAlchemy Session
    user = User(username="test", email="test@test.com")
    db.add(user)
    db.commit()
```

### `client`
创建测试客户端,使用测试数据库。

```python
def test_api(client):
    response = client.get("/api/v1/goals")
    assert response.status_code == 200
```

### `test_user`
创建测试用户。

```python
def test_with_user(test_user):
    assert test_user.username == "testuser"
```

### `auth_headers`
创建认证请求头。

```python
def test_authenticated(client, auth_headers):
    response = client.get("/api/v1/conversations", headers=auth_headers)
    assert response.status_code == 200
```

### `test_goal`
创建测试目标。

```python
def test_with_goal(test_goal):
    assert test_goal.title == "学习 Python"
```

### `test_plan`
创建测试规划。

### `test_task`
创建测试任务。

## 测试最佳实践

### 1. 测试命名规范

- 测试文件名: `test_<module_name>.py`
- 测试类名: `Test<ClassName>`
- 测试方法名: `test_<what>_<expected>`

示例:
```python
def test_create_conversation_success():
    """测试创建对话 - 成功场景"""
    pass

def test_create_conversation_invalid_data():
    """测试创建对话 - 数据无效"""
    pass
```

### 2. AAA 模式

每个测试遵循 AAA (Arrange-Act-Assert) 模式:

```python
def test_create_task(client, auth_headers, test_goal):
    # Arrange (准备)
    task_data = {
        "goal_id": test_goal.id,
        "title": "测试任务",
        "due_date": "2026-03-10"
    }

    # Act (执行)
    response = client.post("/api/v1/tasks", json=task_data, headers=auth_headers)

    # Assert (断言)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "测试任务"
```

### 3. 数据隔离

每个测试独立运行,不依赖其他测试:

```python
# ❌ 错误: 依赖其他测试创建的数据
def test_get_tasks():
    # 假设任务已经在其他测试中创建
    pass

# ✅ 正确: 在测试中创建所需数据
def test_get_tasks(client, auth_headers, test_goal):
    # 创建任务
    client.post("/api/v1/tasks", json={...}, headers=auth_headers)

    # 获取任务
    response = client.get("/api/v1/tasks", headers=auth_headers)
    assert len(response.json()["tasks"]) > 0
```

### 4. 边界测试

测试边界条件和异常场景:

```python
def test_create_event_invalid_time(client, auth_headers):
    """测试创建日程 - 时间无效"""
    response = client.post(
        "/api/v1/events",
        json={
            "start_time": "16:00:00",  # 开始晚于结束
            "end_time": "14:00:00"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
```

## 常见问题

### 1. 测试数据库锁定

如果遇到数据库锁定问题,确保每个测试使用独立的数据库会话:

```python
@pytest.fixture(scope="function")
def db():
    # 每个测试函数使用新的会话
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
```

### 2. 异步测试

对于异步函数,使用 `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### 3. Mock外部服务

对于外部API调用(如OpenAI),使用Mock:

```python
from unittest.mock import patch, AsyncMock

@patch('app.services.ai_service.openai.chat.completions.create')
async def test_ai_conversation(mock_create, client, auth_headers):
    # Mock OpenAI响应
    mock_create.return_value = AsyncMock(
        choices=[Mock(message=Mock(content="AI回复"))]
    )

    response = client.post("/api/v1/conversations/1/messages", ...)
    assert response.status_code == 201
```

## 持续集成

### GitHub Actions 配置示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 测试报告

### 生成HTML覆盖率报告

```bash
pytest tests/ --cov=app --cov-report=html
# 报告在 htmlcov/index.html
```

### 生成JSON报告

```bash
pytest tests/ --json-report --json-report-file=test-report.json
```

## 贡献指南

添加新测试时:

1. 确保测试命名清晰明确
2. 遵循AAA模式
3. 包含正常流程和异常场景
4. 使用合适的Fixtures
5. 添加清晰的文档字符串

## 联系方式

如有测试相关问题,请联系开发团队或查看项目文档。
