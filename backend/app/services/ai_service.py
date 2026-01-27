"""
AI 规划生成服务 - 使用 LLMOperator
"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.core.logger import logger
from app.core.config import settings
from app.utils.llm_operator import LLMOperator


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
- 期望完成时间：{deadline if deadline else '未指定'}
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
"""
    return prompt


class AIService:
    """AI 规划生成服务"""

    def __init__(self):
        """初始化 AI 客户端"""
        # 只有配置了 API Key 才初始化客户端
        if settings.LLM_MODEL_API_KEY:
            try:
                self.llm_operator = LLMOperator(
                    model_name=settings.LLM_MODEL_NAME,
                    api_key=settings.LLM_MODEL_API_KEY,
                    base_url=settings.LLM_MODEL_BASE_URL,
                    api_type=settings.LLM_MODEL_API_TYPE
                )
                self.llm = self.llm_operator.get_llm()
                logger.info(f"AI 服务初始化成功，模型: {settings.LLM_MODEL_NAME}")
            except Exception as e:
                logger.error(f"AI 服务初始化失败: {e}")
                self.llm = None
                self.llm_operator = None
        else:
            self.llm = None
            self.llm_operator = None
            logger.warning("未配置 LLM_MODEL_API_KEY，AI 服务将使用降级方案")

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
        # 如果未配置 API Key，使用降级方案
        if not self.llm:
            logger.info("使用降级方案生成规划")
            return self._get_fallback_plan(goal_title)

        try:
            # 生成 Prompt
            prompt = generate_prompt(goal_title, goal_description, deadline, available_hours)

            # 调用 AI API
            logger.info(f"调用 AI 生成规划，目标：{goal_title}")

            # 构建消息
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]

            # 调用 LangChain LLM
            response = self.llm.invoke(messages)
            content = response.content

            # 解析 JSON
            plan_data = json.loads(content)

            # 验证数据格式
            self._validate_plan_data(plan_data)

            logger.info(f"规划生成成功，包含 {len(plan_data.get('stages', []))} 个阶段")

            return plan_data

        except json.JSONDecodeError as e:
            logger.error(f"AI 返回的 JSON 格式错误：{e}")
            # 使用降级方案
            logger.info("使用降级方案生成规划")
            return self._get_fallback_plan(goal_title)

        except Exception as e:
            logger.error(f"AI 调用失败：{e}")
            # 使用降级方案
            logger.info("使用降级方案生成规划")
            return self._get_fallback_plan(goal_title)

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

    def _get_fallback_plan(self, goal_title: str) -> Dict[str, Any]:
        """
        获取备用规划（模板）

        Args:
            goal_title: 目标标题

        Returns:
            规划 JSON 数据
        """
        return {
            "stages": [
                {
                    "name": "准备阶段",
                    "order": 1,
                    "description": "收集资料和制定计划",
                    "tasks": [
                        {
                            "title": f"收集 {goal_title} 相关资料",
                            "description": "查找相关的教程、文档、视频",
                            "estimated_hours": 2.0,
                            "order": 1
                        },
                        {
                            "title": "制定详细计划",
                            "description": "将目标分解为更小的任务",
                            "estimated_hours": 1.0,
                            "order": 2
                        },
                        {
                            "title": "准备学习/工作环境",
                            "description": "配置所需的工具和资源",
                            "estimated_hours": 1.0,
                            "order": 3
                        }
                    ]
                },
                {
                    "name": "执行阶段",
                    "order": 2,
                    "description": "按计划执行任务",
                    "tasks": [
                        {
                            "title": "开始执行第一个任务",
                            "description": "按照计划开始行动",
                            "estimated_hours": 2.0,
                            "order": 1
                        },
                        {
                            "title": "持续学习和实践",
                            "description": "每天按计划学习和实践",
                            "estimated_hours": 2.0,
                            "order": 2
                        },
                        {
                            "title": "记录学习笔记",
                            "description": "总结学习心得和遇到的问题",
                            "estimated_hours": 1.0,
                            "order": 3
                        }
                    ]
                },
                {
                    "name": "总结阶段",
                    "order": 3,
                    "description": "复盘和总结",
                    "tasks": [
                        {
                            "title": "回顾整个学习过程",
                            "description": "总结成功经验和不足",
                            "estimated_hours": 1.0,
                            "order": 1
                        },
                        {
                            "title": "制定下一步计划",
                            "description": "根据学习成果制定后续目标",
                            "estimated_hours": 1.0,
                            "order": 2
                        }
                    ]
                }
            ]
        }


# 全局实例
ai_service = AIService()
