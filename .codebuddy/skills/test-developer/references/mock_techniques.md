# Mock 技术指南

## 基础 Mock

```python
from unittest.mock import Mock

# 创建 Mock 对象
mock = Mock()

# 配置返回值
mock.method.return_value = 42
result = mock.method()  # 返回 42

# 配置副作用
mock.method.side_effect = Exception("Error")
mock.method()  # 抛出异常

# 配置多次调用返回不同值
mock.method.side_effect = [1, 2, 3]
assert mock.method() == 1
assert mock.method() == 2
assert mock.method() == 3
```

## 断言 Mock 调用

```python
mock = Mock()

# 断言方法被调用
mock.method()
mock.method.assert_called_once()

# 断言方法被特定参数调用
mock.method(arg1, arg2)
mock.method.assert_called_with(arg1, arg2)

# 断言调用次数
assert mock.method.call_count == 2

# 查看调用历史
print(mock.method.call_args_list)
```

## Patch

```python
from unittest.mock import patch

# 使用装饰器 patch
@patch('app.services.external_api')
def test_with_patch(mock_api):
    mock_api.get.return_value = {"data": "test"}
    result = my_function()
    mock_api.get.assert_called_once()

# 使用上下文管理器 patch
def test_with_patch_context():
    with patch('app.services.external_api') as mock_api:
        mock_api.get.return_value = {"data": "test"}
        result = my_function()
        mock_api.get.assert_called_once()

# Patch 类方法
@patch('app.models.User.query')
def test_with_patch_class(mock_query):
    mock_query.filter.return_value.first.return_value = user
    result = get_user(1)
    mock_query.filter.assert_called_once()
```

## MagicMock

```python
from unittest.mock import MagicMock

# MagicMock 支持魔术方法
mock = MagicMock()
mock[0] = "value"
assert mock[0] == "value"

mock.__len__.return_value = 5
assert len(mock) == 5

mock.__str__.return_value = "mocked"
assert str(mock) == "mocked"
```

## Spec 模式

```python
# 使用 spec 让 Mock 表现得像真实对象
class RealClass:
    def method(self):
        pass

mock = Mock(spec=RealClass)
mock.method()  # OK
mock.nonexistent()  # AttributeError

# 使用 spec_set 严格模式
mock = Mock(spec_set=RealClass)
mock.method()  # OK
mock.nonexistent()  # AttributeError
```

## 异步 Mock

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_mock():
    mock = AsyncMock()
    mock.return_value = "result"
    result = await mock()
    assert result == "result"
```

## Property Mock

```python
from unittest.mock import PropertyMock

class MyClass:
    @property
    def my_property(self):
        return "real value"

# Mock 属性
mock_obj = MyClass()
with patch.object(mock_obj.__class__, 'my_property', new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = "mocked value"
    assert mock_obj.my_property == "mocked value"
```

## 在 Pytest 中使用 Mock

```python
@pytest.fixture
def mock_external_service():
    """Mock 外部服务 fixture"""
    mock = Mock()
    mock.get_data.return_value = {"result": "success"}
    return mock

def test_with_mock_fixture(mock_external_service):
    result = my_function(mock_external_service)
    mock_external_service.get_data.assert_called_once()
```

## 常见场景

### Mock 数据库查询

```python
@patch('app.models.User.query')
def test_get_user(mock_query):
    user = User(id=1, username="test")
    mock_query.filter.return_value.first.return_value = user
    result = get_user(1)
    assert result.username == "test"
```

### Mock 外部 API

```python
@patch('app.services.requests.get')
def test_external_api(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = call_external_api()
    mock_get.assert_called_once_with("https://api.example.com/data")
```

### Mock 时间

```python
from unittest.mock import patch
from datetime import datetime

@patch('app.utils.datetime')
def test_with_mocked_time(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 1)
    result = get_current_time()
    assert result == datetime(2024, 1, 1)
```

### Mock 文件操作

```python
@patch('builtins.open')
def test_file_operation(mock_open):
    mock_file = MagicMock()
    mock_file.read.return_value = "file content"
    mock_open.return_value.__enter__.return_value = mock_file

    result = read_file("test.txt")
    assert result == "file content"
    mock_open.assert_called_once_with("test.txt", "r")
```

## 注意事项

### ✅ 应该 Mock
- 外部 API 调用
- 数据库操作（在单元测试中）
- 文件系统操作
- 时间依赖的代码
- 慢速操作

### ❌ 不应该 Mock
- 被测试的代码本身
- 简单的数据结构
- 已经验证过的库函数
- 配置和常量

### 避免过度 Mock
```python
# ❌ 不好：过度 Mock，测试价值低
@patch('module.func_a')
@patch('module.func_b')
@patch('module.func_c')
def test_over_mocked(mock_a, mock_b, mock_c):
    # 测试的是 Mock 而不是真实逻辑
    pass

# ✅ 好：只 Mock 外部依赖
@patch('module.external_api')
def test_focused(mock_api):
    # 测试真实逻辑
    result = my_function()
    assert result is not None
```
