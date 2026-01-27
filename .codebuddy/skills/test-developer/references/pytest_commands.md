# Pytest 命令速查

## 基础命令

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_auth.py

# 运行特定类
pytest tests/test_auth.py::TestAuth

# 运行特定测试
pytest tests/test_auth.py::TestAuth::test_login_success
```

## 显示选项

```bash
# 详细输出
pytest -v

# 显示打印输出
pytest -s

# 显示最慢的 10 个测试
pytest --durations=10
```

## 选择测试

```bash
# 只运行上次失败的测试
pytest --lf

# 先运行上次失败的测试
pytest --ff

# 运行特定标记的测试
pytest -m unit
pytest -m "not slow"
```

## 执行控制

```bash
# 遇到第一个失败就停止
pytest -x

# 遇到第 N 个失败就停止
pytest --maxfail=3

# 停止在第一个错误（非失败）
pytest --exitfirst
```

## 覆盖率

```bash
# 生成覆盖率报告
pytest --cov=app

# 生成 HTML 报告
pytest --cov=app --cov-report=html

# 生成终端报告
pytest --cov=app --cov-report=term-missing

# 仅显示未覆盖的文件
pytest --cov=app --cov-report=term-missing:skip-covered
```

## 并行执行

```bash
# 使用所有 CPU 核心
pytest -n auto

# 使用指定数量的进程
pytest -n 4
```

## 调试

```bash
# 失败时进入 pdb
pytest --pdb

# 失败时进入 ipdb
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb --pdb

# 在第一个失败时进入调试器
pytest --pdb --trace
```

## 其他选项

```bash
# 运行测试并显示警告
pytest -W error

# 跳过慢速测试
pytest -m "not slow"

# 显示测试的本地变量
pytest -l
```
