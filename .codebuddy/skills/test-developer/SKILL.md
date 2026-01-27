# 单元测试开发专家

专业的单元测试开发专家，精通 Python 测试框架（pytest）、测试最佳实践、测试覆盖率优化、Mock 技术、集成测试等。适用于编写高质量、可维护的测试代码、提升代码质量、保障系统稳定性等场景。

## 核心能力

### 1. 测试框架使用

#### Pytest 基础
- ✅ 熟练使用 pytest 及其丰富的插件生态
- ✅ 理解 fixture 机制和依赖注入
- ✅ 掌握参数化测试、标记测试、跳过测试
- ✅ 了解测试发现、收集和执行机制

#### 测试断言
- ✅ 使用标准 assert 语句
- ✅ 理解异常测试和警告测试
- ✅ 掌握近似值比较和集合比较

### 2. 测试设计原则

#### 测试金字塔
```
      /\
     /E2E\        - 端到端测试（少量）
    /------\
   /集成测试\      - 集成测试（适量）
  /----------\
 /  单元测试  \    - 单元测试（大量）
--------------
```

#### 测试覆盖
- ✅ 单元测试：测试单个函数/方法的行为
- ✅ 集成测试：测试多个组件协作
- ✅ 端到端测试：测试完整用户流程

#### 测试命名规范
```python
def test_<被测功能>_<期望结果>_<条件>():
    """
    示例：
    test_login_success_with_valid_credentials()
    test_login_failure_with_invalid_password()
    test_get_user_by_id_returns_user_when_exists()
    """
    pass
```

### 3. 测试隔离

#### 数据库隔离
- 使用内存数据库进行测试
- 每个测试独立的数据库会话
- 自动回滚事务

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 使用内存数据库
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    """每个测试函数独立的数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

#### 外部依赖隔离
- 使用 Mock/patch 模拟外部服务
- 使用 Fake 对象替代复杂依赖
- 隔离文件系统、网络、时间等

```python
from unittest.mock import Mock, patch

@pytest.fixture
def mock_external_service():
    """Mock 外部服务"""
    service = Mock()
    service.get_data.return_value = {"result": "success"}
    return service

def test_with_mock(mock_external_service):
    result = my_function(mock_external_service)
    assert result["result"] == "success"
```

### 4. 测试覆盖率

#### 覆盖率指标
- **行覆盖率**：执行的代码行数比例
- **分支覆盖率**：执行的分支条件比例
- **函数覆盖率**：调用的函数比例

#### 目标要求
- 核心业务逻辑：≥ 90%
- 工具函数：≥ 80%
- 整体项目：≥ 70%

#### 生成覆盖率报告
```bash
# 生成 HTML 报告
pytest --cov=app --cov-report=html

# 生成终端报告
pytest --cov=app --cov-report=term-missing

# 仅显示未覆盖的行
pytest --cov=app --cov-report=term-missing:skip-covered
```

### 5. Fixtures 最佳实践

#### Fixture 作用域
```python
@pytest.fixture(scope="function")  # 每个测试函数执行一次（默认）
@pytest.fixture(scope="class")     # 每个测试类执行一次
@pytest.fixture(scope="module")    # 每个模块执行一次
@pytest.fixture(scope="session")   # 整个测试会话执行一次
```

#### Fixture 依赖
```python
@pytest.fixture
def db():
    """数据库会话"""
    return create_db()

@pytest.fixture
def user(db):
    """测试用户（依赖 db）"""
    return create_user(db)

def test_something(user):
    """使用 user fixture"""
    pass
```

#### Fixture 参数化
```python
@pytest.fixture(params=["user", "admin", "guest"])
def user_role(request):
    """参数化的用户角色"""
    return request.param

def test_with_roles(user_role):
    """每个角色都会执行一次"""
    assert user_role in ["user", "admin", "guest"]
```

### 6. Mock 技术

#### 使用 unittest.mock
```python
from unittest.mock import Mock, patch, MagicMock

# 创建 Mock 对象
mock = Mock()
mock.method.return_value = 42
mock.method.assert_called_once()

# Patch 装饰器
@patch('app.services.external_api')
def test_with_patch(mock_api):
    mock_api.get.return_value = {"data": "test"}
    result = my_function()
    mock_api.get.assert_called_once()

# Patch 上下文管理器
def test_with_patch_context():
    with patch('app.services.external_api') as mock_api:
        mock_api.get.return_value = {"data": "test"}
        result = my_function()
```

#### 使用 pytest-mock
```python
@pytest.fixture
def mocker():
    return pytest.importorskip("pytest_mock").mocker

def test_with_pytest_mock(mocker):
    mock_func = mocker.patch('app.services.external_api')
    mock_func.get.return_value = {"data": "test"}
```

### 7. 异步测试

#### 测试异步代码
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

@pytest.mark.asyncio
async def test_async_client(async_client):
    response = await async_client.get("/api/endpoint")
    assert response.status_code == 200
```

### 8. 测试组织

#### 目录结构
```
tests/
├── __init__.py
├── conftest.py              # 共享 fixtures
├── unit/                    # 单元测试
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/              # 集成测试
│   ├── test_api.py
│   └── test_database.py
└── e2e/                     # 端到端测试
    └── test_user_flow.py
```

#### 测试标记
```python
import pytest

@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_long_running():
    pass

# 运行特定标记的测试
# pytest -m unit
# pytest -m "not slow"
```

### 9. 测试数据库

#### 使用测试数据库
```python
@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

#### 测试数据工厂
```python
@pytest.fixture
def test_user_factory():
    """测试用户工厂"""
    def create_user(username, email):
        return User(
            username=username,
            email=email,
            password_hash=hash_password("password123")
        )
    return create_user

def test_with_factory(test_user_factory):
    user1 = test_user_factory("user1", "user1@example.com")
    user2 = test_user_factory("user2", "user2@example.com")
    assert user1.username != user2.username
```

### 10. API 测试

#### FastAPI 测试
```python
from fastapi.testclient import TestClient

@pytest.fixture
def client(test_db):
    """测试客户端"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

def test_create_user(client):
    response = client.post(
        "/api/users",
        json={"username": "test", "email": "test@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test"
```

#### 带认证的测试
```python
@pytest.fixture
def auth_headers(client):
    """认证请求头"""
    # 先注册/登录获取 token
    response = client.post(
        "/api/auth/login",
        json={"username": "test", "password": "password"}
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}

def test_protected_endpoint(client, auth_headers):
    response = client.get("/api/goals", headers=auth_headers)
    assert response.status_code == 200
```

### 11. 测试最佳实践

#### ✅ 应该做的
1. **测试独立性**：每个测试应该独立运行
2. **可读性**：测试代码应该清晰易懂
3. **测试行为而非实现**：关注"做什么"而非"怎么做"
4. **使用有意义的断言消息**
5. **保持测试简单**：避免复杂的测试逻辑

#### ❌ 不应该做的
1. **不要测试第三方库**：相信库作者已经测试过
2. **不要写有副作用的测试**：不要修改真实数据库
3. **不要过度使用 Mock**：Mock 太多会降低测试价值
4. **不要忽略测试失败**：及时修复测试
5. **不要在测试中写业务逻辑**

### 12. 测试性能优化

#### 并行测试
```python
# 安装 pytest-xdist
pip install pytest-xdist

# 使用多核运行测试
pytest -n auto

# 指定使用 4 个进程
pytest -n 4
```

#### 测试缓存
```python
@pytest.fixture(scope="session")
def heavy_resource():
    """昂贵的资源，整个会话只创建一次"""
    return create_heavy_resource()
```

### 13. 调试测试

#### 失败时进入 pdb
```bash
pytest --pdb
```

#### 失败时进入 ipdb
```bash
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb --pdb
```

#### 打印输出
```bash
pytest -s  # 不捕获输出，显示 print
```

#### 只运行失败的测试
```bash
pytest --lf  # last-failed
```

### 14. 持续集成

#### CI 配置示例（GitHub Actions）
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
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 工作流程

### 编写新功能的测试
1. 先编写测试用例（TDD）
2. 运行测试，确认失败
3. 实现功能代码
4. 运行测试，确认通过
5. 重构代码，保持测试通过

### 修复 Bug 的测试
1. 编写复现 Bug 的测试用例
2. 运行测试，确认失败
3. 修复 Bug
4. 运行测试，确认通过
5. 检查是否有相关测试失败

### 重构代码的测试
1. 运行完整测试套件，确认全部通过
2. 进行重构
3. 运行测试，确认仍然通过
4. 如果测试失败，回滚重构或修复测试

## 常用命令

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_auth.py

# 运行特定类
pytest tests/test_auth.py::TestAuth

# 运行特定测试
pytest tests/test_auth.py::TestAuth::test_login_success

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s

# 停止在第一个失败
pytest -x

# 并行运行
pytest -n auto

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 只运行上次失败的测试
pytest --lf

# 运行特定标记的测试
pytest -m unit
pytest -m "not slow"
```

## 推荐插件

- **pytest-cov**: 覆盖率统计
- **pytest-asyncio**: 异步测试支持
- **pytest-xdist**: 并行测试
- **pytest-mock**: Mock 功能增强
- **pytest-html**: HTML 测试报告
- **pytest-timeout**: 超时控制
- **pytest-benchmark**: 性能测试
