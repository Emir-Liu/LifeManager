---
name: Python后端开发工程师
description: 专业的Python后端开发专家,精通FastAPI/Flask/Django框架、数据库操作、LLM集成、任务队列。适用于SOP引擎类复杂后端服务开发、API设计、异步任务处理等场景。
---

# Python后端开发工程师技能

## 概述

本技能提供专业的Python后端开发能力,特别针对SOP引擎等复杂业务场景,涵盖分层架构、设计模式、LLM集成、异步任务处理等核心能力。

## 何时使用本技能

- 需要开发FastAPI后端服务
- 需要集成LLM(OpenAI/Qwen3等)
- 需要实现异步任务处理
- 需要设计分层架构
- 需要实现Redis Streams任务队列
- 需要使用抽象基类和设计模式
- 需要优化LLM调用和Token管理

## 核心能力

### 1. 分层架构实现

采用**API→Func→Core→Utils**四层架构:

- **API层**: 接口定义、参数验证、响应封装
- **Func层**: 业务逻辑组装、任务编排、状态管理
- **Core层**: 核心算法实现、抽象基类、复杂业务逻辑
- **Utils层**: 通用工具类、基础设施、第三方封装

### 2. 设计模式应用

- **抽象基类**: 定义统一接口,复用通用代码
- **混入类(Mixin)**: 功能组合,避免继承过深
- **工厂模式**: 动态创建对象,解耦类型选择
- **DTO模式**: 统一数据传输和状态管理

### 3. LLM集成

使用LangChain集成多种LLM:
- OpenAI兼容接口
- Qwen3等本地模型
- Token使用统计
- 重试机制和错误处理

### 4. 异步任务处理

- 线程池管理(见`assets/task_manager_template.py`)
- Redis Streams任务队列
- 任务状态跟踪
- 回调机制

### 5. 长文本处理

- 对话切片策略
- 摘要生成
- 结果合并

## 快速开始

### 创建FastAPI项目

参考`assets/`目录下的模板代码:

**基础工具类:**
- `file_operator.py` - 文件保存/读取/JSON处理
- `time_operator.py` - 计时器/时间格式化
- `id_generator.py` - UUID和业务ID生成
- `redis_stream_handler.py` - Redis Stream消息队列

**核心模板:**
- `llm_config_template.py` - LLM配置和回调
- `task_manager_template.py` - 任务管理器

### 查阅设计思路

- `references/design_patterns.md` - 设计模式和架构模式详解
- `references/utility_classes.md` - 工具类设计和使用指南

### 使用示例

```python
# 1. 创建LLM
from assets.llm_config_template import create_llm_qwen3, TokenUsageCallback
llm = create_llm_qwen3(
    model_name="qwen3-32b-awq",
    api_key="your_key",
    base_url="http://localhost:8000"
)

# 2. 使用任务管理器
from assets.task_manager_template import TaskWorker
with TaskWorker(max_workers=5) as worker:
    worker.submit_task("task_1", process_func, data)

# 3. 应用设计模式
from references.design_patterns import BatchAnalyzerMixin
class MyAnalyzer(BatchAnalyzerMixin):
    pass  # 自动获得批量处理能力
```

## SOP引擎特定技能

### 业务流程

1. **SOP模板提取**: PDF/DOCX解析 → LLM提取 → MinIO存储
2. **对话分类**: 读取对话 → LLM分类 → 结果存储
3. **对话验证**: 步骤验证 + 禁忌语检测 + 敏感词检测

### 关键技术

- Pydantic数据验证
- SQLAlchemy ORM
- MinIO对象存储
- Redis Streams消费者组
- LangChain Prompt模板

## 持续自我提升

在执行任务过程中,本技能将根据执行结果不断优化自身能力:

### 执行结果分析
- **代码质量**: 通过代码审查和测试结果,识别常见问题和改进点
- **性能数据**: 收集API响应时间、内存使用等指标,优化代码实现
- **错误模式**: 分析生产环境的错误日志,总结常见问题和解决方案
- **新技术应用**: 评估新引入的技术效果,更新技术栈知识

### 能力提升方向
1. **架构设计**: 根据项目复杂度,优化分层架构和设计模式应用
2. **代码效率**: 总结性能优化技巧,建立最佳实践库
3. **错误处理**: 建立更完善的错误分类和处理策略
4. **测试覆盖**: 提升测试覆盖率,优化测试用例设计
5. **LLM优化**: 根据实际使用效果,优化Prompt设计和Token管理策略

### 持续改进机制
- 记录每次开发中遇到的技术难点和解决方案
- 建立代码模板和最佳实践库
- 定期审查和重构旧代码
- 学习新的Python特性和框架更新
- 将经验转化为可复用的模板和工具

## 质量检查清单

- [ ] 符合分层架构原则
- [ ] 使用抽象基类定义接口
- [ ] LLM调用包含Token统计
- [ ] 长文本使用切片处理
- [ ] 异常使用细粒度错误码
- [ ] 任务状态统一管理
- [ ] 日志分级记录
- [ ] 配置环境隔离
