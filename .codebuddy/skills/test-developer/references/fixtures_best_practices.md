# Pytest Fixtures 最佳实践

## Fixture 基础

```python
import pytest

@pytest.fixture
def simple_fixture():
    """最简单的 fixture"""
    return {"key": "value"}

def test_with_fixture(simple_fixture):
    assert simple_fixture["key"] == "value"
```

## Fixture 作用域

```python
@pytest.fixture(scope="function")  # 默认，每个测试函数执行一次
def func_scope():
    pass

@pytest.fixture(scope="class")     # 每个测试类执行一次
def class_scope():
    pass

@pytest.fixture(scope="module")    # 每个模块执行一次
def module_scope():
    pass

@pytest.fixture(scope="session")   # 整个测试会话执行一次
def session_scope():
    pass
```

## Fixture 依赖

```python
@pytest.fixture
def db():
    """创建数据库会话"""
    return create_db()

@pytest.fixture
def user(db):
    """创建测试用户（依赖 db）"""
    return User(username="test", db=db)

@pytest.fixture
def post(user):
    """创建测试文章（依赖 user）"""
    return Post(title="Test", user=user)

def test_post_content(post):
    assert post.title == "Test"
```

## Yield Fixtures

```python
@pytest.fixture
def db_session():
    """使用 yield 的 fixture"""
    session = create_session()
    yield session  # 传递给测试
    session.close()  # 清理代码
```

## 参数化 Fixtures

```python
@pytest.fixture(params=["user", "admin", "guest"])
def user_role(request):
    """参数化的 fixture，每个参数执行一次测试"""
    return request.param

def test_with_roles(user_role):
    """这个测试会运行 3 次"""
    assert user_role in ["user", "admin", "guest"]
```

## 自动使用 Fixtures

```python
@pytest.fixture(autouse=True)
def setup_database():
    """自动使用的 fixture，无需在测试参数中声明"""
    print("Setup database")
    yield
    print("Teardown database")

def test_without_explicit_fixture():
    """不需要声明 fixture 参数"""
    assert True
```

## Factory Fixtures

```python
@pytest.fixture
def user_factory():
    """工厂函数 fixture"""
    def create_user(username, email):
        return User(username=username, email=email)
    return create_user

def test_with_factory(user_factory):
    user1 = user_factory("user1", "user1@example.com")
    user2 = user_factory("user2", "user2@example.com")
    assert user1.username != user2.username
```

## Mock Fixtures

```python
@pytest.fixture
def mock_external_api():
    """Mock 外部 API"""
    with patch('app.api.external') as mock:
        mock.get.return_value = {"data": "test"}
        yield mock

def test_with_mock(mock_external_api):
    result = call_external_api()
    mock_external_api.get.assert_called_once()
```

## 数据库 Fixtures

```python
@pytest.fixture(scope="function")
def test_db():
    """测试数据库"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    """测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user
```

## 客户端 Fixtures

```python
@pytest.fixture
def client(test_db):
    """FastAPI 测试客户端"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
```

## 认证 Fixtures

```python
@pytest.fixture
def auth_headers(client):
    """认证请求头"""
    response = client.post(
        "/api/auth/login",
        json={"username": "test", "password": "password"}
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
```

## 使用 conftest.py

```python
# tests/conftest.py

# 共享的 fixtures 可以放在这里，所有测试文件都可以使用

@pytest.fixture(scope="session")
def global_config():
    """整个测试会话的配置"""
    return load_config()

@pytest.fixture(scope="function")
def test_data():
    """测试数据"""
    return {"key": "value"}
```
