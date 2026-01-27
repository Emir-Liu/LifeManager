# LifeManager MVP AI 集成文档

## 文档信息

- **版本**: v1.0
- **创建日期**: 2026-01-27
- **作者**: 产品经理
- **状态**: 已发布
- **适用阶段**: Phase 1 - MVP

---

## 1. AI 服务概述

### 1.1 AI 选型

**主选方案**: DeepSeek API

**备用方案**: OpenAI API

**选型理由**:
- ✅ DeepSeek 成本更低（约 OpenAI 的 1/10）
- ✅ 对中文支持更好
- ✅ 兼容 OpenAI API 格式
- ✅ 提供 128k 上下文窗口

### 1.2 环境变量配置

```bash
# backend/.env
OPENAI_API_BASE=https://api.deepseek.com
OPENAI_API_KEY=sk-xxx  # DeepSeek API Key
AI_MODEL=deepseek-chat
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7
```

---

## 2. AI Prompt 设计

### 2.1 基础 Prompt 模板

```python
# backend/app/services/ai_service.py

SYSTEM_PROMPT = """
你是一个专业的目标规划助手，擅长将长期目标分解为可执行的短期任务。

你的任务：
1. 分析用户的目标和约束条件
2. 将目标分解为 3-5 个阶段
3. 每个阶段分解为具体的任务
4. 估算每个任务的时间（小时）
5. 确保任务之间的逻辑顺序合理

输出要求：
1. 必须返回标准的 JSON 格式
2. 阶段数量：3-5 个
3. 每个阶段任务数：3-8 个
4. 任务描述简洁明确
5. 时间估算合理（不要太乐观）
"""

def generate_prompt(goal_title: str, goal_description: str, deadline: str, available_hours: int) -> str:
    """
    生成 AI Prompt

    Args:
        goal_title: 目标标题
        goal_description: 目标描述
        deadline: 截止日期 (YYYY-MM-DD)
        available_hours: 每天可用小时数

    Returns:
        Prompt 文本
    """
    prompt = f"""
请根据以下信息，生成一个详细的执行规划：

## 目标信息
- 目标名称：{goal_title}
- 目标描述：{goal_description}
- 期望完成时间：{deadline}
- 每天可用时间：约 {available_hours} 小时

## 要求
1. 将目标分解为 3-5 个阶段（按时间顺序）
2. 每个阶段分解为 3-8 个具体任务
3. 估算每个任务的预估时间（小时）
4. 任务之间有合理的逻辑依赖
5. 考虑学习曲线和难度递增

## 输出格式
请严格按照以下 JSON 格式输出（不要添加其他文字）：

{{
  "stages": [
    {{
      "name": "阶段名称",
      "order": 1,
      "description": "阶段描述（可选）",
      "tasks": [
        {{
          "title": "任务标题",
          "description": "任务描述（可选）",
          "estimated_hours": 2.0,
          "order": 1
        }}
      ]
    }}
  ]
}}

## 示例
如果用户目标是"学习 Python 编程"，期望在 3 个月内完成，每天 2 小时：

{{
  "stages": [
    {{
      "name": "第一阶段：基础语法学习",
      "order": 1,
      "description": "掌握 Python 基础语法和核心概念",
      "tasks": [
        {{
          "title": "安装 Python 环境",
          "description": "下载并安装 Python 3.10+ 和 IDE",
          "estimated_hours": 0.5,
          "order": 1
        }},
        {{
          "title": "学习变量和数据类型",
          "description": "理解整数、浮点数、字符串、列表等",
          "estimated_hours": 2.0,
          "order": 2
        }},
        {{
          "title": "学习控制流语句",
          "description": "掌握 if/else、for 循环、while 循环",
          "estimated_hours": 3.0,
          "order": 3
        }},
        {{
          "title": "学习函数定义",
          "description": "理解函数参数、返回值、作用域",
          "estimated_hours": 3.0,
          "order": 4
        }},
        {{
          "title": "完成基础练习题",
          "description": "LeetCode 基础题目 10 道",
          "estimated_hours": 4.0,
          "order": 5
        }}
      ]
    }},
    {{
      "name": "第二阶段：进阶特性学习",
      "order": 2,
      "description": "掌握 Python 进阶特性和常用库",
      "tasks": [
        {{
          "title": "学习面向对象编程",
          "description": "类、对象、继承、多态",
          "estimated_hours": 4.0,
          "order": 1
        }},
        {{
          "title": "学习文件操作",
          "description": "读写文件、文件路径处理",
          "estimated_hours": 2.0,
          "order": 2
        }},
        {{
          "title": "学习异常处理",
          "description": "try/except、自定义异常",
          "estimated_hours": 2.0,
          "order": 3
        }},
        {{
          "title": "学习标准库",
          "description": "datetime, json, re, os 等常用库",
          "estimated_hours": 4.0,
          "order": 4
        }}
      ]
    }},
    {{
      "name": "第三阶段：实战项目",
      "order": 3,
      "description": "通过实际项目巩固所学知识",
      "tasks": [
        {{
          "title": "项目一：计算器程序",
          "description": "实现基础四则运算计算器",
          "estimated_hours": 4.0,
          "order": 1
        }},
        {{
          "title": "项目二：待办事项应用",
          "description": "命令行版本的 Todo List",
          "estimated_hours": 6.0,
          "order": 2
        }},
        {{
          "title": "项目三：爬虫程序",
          "description": "爬取网页数据并保存",
          "estimated_hours": 8.0,
          "order": 3
        }},
        {{
          "title": "代码优化和重构",
          "description": "优化代码质量，添加注释",
          "estimated_hours": 4.0,
          "order": 4
        }}
      ]
    }}
  ]
}}
"""
    return prompt
```

---

## 3. AI 服务实现

### 3.1 AI 服务类

```python
# backend/app/services/ai_service.py

import os
import json
from typing import Dict, Any
from openai import OpenAI
from app.core.logger import logger

class AIService:
    """AI 规划生成服务"""

    def __init__(self):
        """初始化 AI 客户端"""
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com")
        )
        self.model = os.getenv("AI_MODEL", "deepseek-chat")
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", 4000))
        self.temperature = float(os.getenv("AI_TEMPERATURE", 0.7))

    def generate_plan(
        self,
        goal_title: str,
        goal_description: str,
        deadline: str,
        available_hours: int
    ) -> Dict[str, Any]:
        """
        生成规划

        Args:
            goal_title: 目标标题
            goal_description: 目标描述
            deadline: 截止日期
            available_hours: 每天可用小时数

        Returns:
            规划 JSON 数据

        Raises:
            ValueError: AI 返回格式错误
            Exception: AI 调用失败
        """
        try:
            # 生成 Prompt
            prompt = generate_prompt(goal_title, goal_description, deadline, available_hours)

            # 调用 AI API
            logger.info(f"调用 AI 生成规划，目标：{goal_title}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}  # 强制返回 JSON
            )

            # 提取响应内容
            content = response.choices[0].message.content

            # 解析 JSON
            plan_data = json.loads(content)

            # 验证数据格式
            self._validate_plan_data(plan_data)

            logger.info(f"规划生成成功，包含 {len(plan_data.get('stages', []))} 个阶段")

            return plan_data

        except json.JSONDecodeError as e:
            logger.error(f"AI 返回的 JSON 格式错误：{e}")
            raise ValueError("AI 返回格式错误，请重试")
        except Exception as e:
            logger.error(f"AI 调用失败：{e}")
            raise Exception(f"AI 服务不可用：{str(e)}")

    def _validate_plan_data(self, plan_data: Dict[str, Any]):
        """
        验证规划数据格式

        Args:
            plan_data: 规划数据

        Raises:
            ValueError: 数据格式错误
        """
        if not isinstance(plan_data, dict):
            raise ValueError("规划数据必须是字典")

        if "stages" not in plan_data:
            raise ValueError("规划数据缺少 stages 字段")

        stages = plan_data["stages"]
        if not isinstance(stages, list) or len(stages) == 0:
            raise ValueError("stages 必须是非空列表")

        if len(stages) < 2 or len(stages) > 6:
            raise ValueError("阶段数量应在 2-6 个之间")

        for i, stage in enumerate(stages):
            if "name" not in stage or "tasks" not in stage:
                raise ValueError(f"阶段 {i+1} 缺少必要字段")

            tasks = stage["tasks"]
            if not isinstance(tasks, list) or len(tasks) == 0:
                raise ValueError(f"阶段 {i+1} 的任务列表为空")

            for j, task in enumerate(tasks):
                if "title" not in task or "estimated_hours" not in task:
                    raise ValueError(f"阶段 {i+1} 任务 {j+1} 缺少必要字段")

                if not isinstance(task["estimated_hours"], (int, float)):
                    raise ValueError(f"任务 {j+1} 的 estimated_hours 必须是数字")


# 全局实例
ai_service = AIService()
```

---

## 4. 任务自动创建算法

### 4.1 日期分配逻辑

```python
# backend/app/services/task_service.py

import datetime
from typing import List
from app.models.goal import Goal
from app.models.plan import Plan
from app.models.task import Task
from app.core.database import SessionLocal

class TaskService:
    """任务自动创建服务"""

    def create_tasks_from_plan(self, plan: Plan, available_hours: int = 2) -> List[Task]:
        """
        根据规划创建任务

        Args:
            plan: 规划对象
            available_hours: 每天可用小时数

        Returns:
            创建的任务列表
        """
        db = SessionLocal()

        try:
            # 解析规划内容
            plan_data = json.loads(plan.content)
            stages = plan_data.get("stages", [])

            # 计算总任务数
            total_tasks = sum(len(stage.get("tasks", [])) for stage in stages)

            # 计算截止日期
            goal = plan.goal
            deadline = goal.deadline
            start_date = datetime.date.today()

            # 计算可用天数
            delta = deadline - start_date
            available_days = delta.days

            if available_days <= 0:
                raise ValueError("截止日期必须晚于今天")

            # 按日期分配任务
            tasks = []
            current_date = start_date
            task_index = 0

            for stage in stages:
                for task_data in stage.get("tasks", []):
                    # 跳过周末（可选）
                    if current_date.weekday() >= 5:  # 周六、周日
                        current_date += datetime.timedelta(days=1)

                    # 创建任务
                    task = Task(
                        goal_id=plan.goal_id,
                        plan_id=plan.id,
                        title=task_data.get("title"),
                        description=task_data.get("description"),
                        estimated_hours=task_data.get("estimated_hours", 0),
                        due_date=datetime.datetime.combine(current_date, datetime.time(9, 0))  # 上午 9 点
                    )
                    db.add(task)
                    tasks.append(task)

                    # 移动到下一天
                    current_date += datetime.timedelta(days=1)

            # 提交到数据库
            db.commit()

            # 更新规划统计信息
            plan.total_stages = len(stages)
            plan.total_tasks = total_tasks
            plan.estimated_total_hours = sum(
                task.get("estimated_hours", 0)
                for stage in stages
                for task in stage.get("tasks", [])
            )
            db.commit()

            logger.info(f"成功创建 {len(tasks)} 个任务")

            return tasks

        except Exception as e:
            db.rollback()
            logger.error(f"创建任务失败：{e}")
            raise
        finally:
            db.close()


# 全局实例
task_service = TaskService()
```

### 4.2 日期分配策略

**策略 1：均匀分配（默认）**
- 所有任务均匀分配到可用天数
- 每天不超过 `available_hours` 小时

**策略 2：按阶段分组**
- 同一阶段的任务尽量集中
- 考虑任务之间的依赖关系

**策略 3：学习曲线调整**
- 初期任务时间较短
- 后期任务时间逐渐增加

**MVP 采用策略 1（均匀分配）**

---

## 5. 错误处理

### 5.1 AI 调用失败

```python
# 错误类型和错误码
AI_ERROR_CODES = {
    "API_KEY_INVALID": 10001,
    "API_QUOTA_EXCEEDED": 10002,
    "AI_SERVICE_UNAVAILABLE": 10003,
    "AI_GENERATION_FAILED": 10004,
    "INVALID_RESPONSE_FORMAT": 10005
}

# 错误处理示例
try:
    plan_data = ai_service.generate_plan(...)
except ValueError as e:
    # JSON 格式错误
    raise HTTPException(
        status_code=400,
        detail={
            "code": AI_ERROR_CODES["INVALID_RESPONSE_FORMAT"],
            "message": str(e)
        }
    )
except Exception as e:
    # AI 服务错误
    raise HTTPException(
        status_code=503,
        detail={
            "code": AI_ERROR_CODES["AI_SERVICE_UNAVAILABLE"],
            "message": "AI 服务暂时不可用，请稍后重试"
        }
    )
```

### 5.2 降级方案

如果 AI 服务不可用，提供模板规划：

```python
def get_fallback_plan(goal_title: str) -> Dict[str, Any]:
    """
    获取备用规划（模板）
    """
    return {
        "stages": [
            {
                "name": "准备阶段",
                "order": 1,
                "tasks": [
                    {
                        "title": f"收集 {goal_title} 相关资料",
                        "description": "查找相关的教程、文档、视频",
                        "estimated_hours": 2,
                        "order": 1
                    },
                    {
                        "title": "制定详细计划",
                        "description": "将目标分解为更小的任务",
                        "estimated_hours": 1,
                        "order": 2
                    }
                ]
            },
            {
                "name": "执行阶段",
                "order": 2,
                "tasks": [
                    {
                        "title": "开始执行第一个任务",
                        "description": "按照计划开始行动",
                        "estimated_hours": 2,
                        "order": 1
                    },
                    {
                        "title": "持续学习和实践",
                        "description": "每天按计划学习和实践",
                        "estimated_hours": 2,
                        "order": 2
                    }
                ]
            }
        ]
    }
```

---

## 6. 测试

### 6.1 单元测试

```python
# tests/test_ai_service.py

import pytest
from app.services.ai_service import AIService

def test_generate_plan():
    service = AIService()

    plan_data = service.generate_plan(
        goal_title="学习 Python",
        goal_description="在 3 个月内掌握 Python",
        deadline="2025-04-26",
        available_hours=2
    )

    assert "stages" in plan_data
    assert len(plan_data["stages"]) >= 2
    assert len(plan_data["stages"][0]["tasks"]) > 0
```

### 6.2 集成测试

```python
# tests/test_plan_generation.py

def test_generate_plan_endpoint(client, token):
    response = client.post(
        "/api/plans/generate",
        json={
            "goal_id": 1,
            "available_hours_per_day": 2
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["code"] == 0
    assert "plan_id" in response.json()["data"]
```

---

## 7. 成本估算

### 7.1 AI API 成本

**DeepSeek 定价**（示例）:
- 输入: ¥0.001 / 1K tokens
- 输出: ¥0.002 / 1K tokens

**单次生成成本估算**:
- Prompt: ~500 tokens
- Response: ~1500 tokens
- 成本: (0.5 × 0.001 + 1.5 × 0.002) / 1000 = ¥0.0035

**1000 次生成成本**: ¥3.5

### 7.2 优化建议

1. **缓存规划**: 相同目标使用缓存
2. **精简 Prompt**: 减少 Prompt 长度
3. **使用更便宜的模型**: 如果有更低成本的选项

---

## 8. 常见问题

### Q1: AI 返回的 JSON 格式错误怎么办？

**答**:
1. 重试生成（最多 3 次）
2. 使用降级方案（模板规划）
3. 提示用户稍后重试

### Q2: 如何控制规划的质量？

**答**:
1. 调整 temperature 参数（0.3-0.7）
2. 在 Prompt 中提供更多示例
3. 增加数据验证逻辑

### Q3: AI 生成时间太长怎么办？

**答**:
1. 使用流式响应（可选）
2. 添加加载动画提示用户
3. 设置超时时间（30 秒）

---

## 9. 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-27 | v1.0 | 初始版本，完成 AI 集成设计 |
