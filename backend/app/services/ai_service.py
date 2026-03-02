"""
AI 规划生成服务 - 使用 LangChain 链式调用
"""
from typing import Dict, Any
from pydantic import BaseModel, Field, field_validator
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from app.core.exceptions import ErrorCode, ERROR_MESSAGES
from app.core.logger import logger
from app.core.config import settings
from app.utils.llm_operator import LLMOperator


# ============ 数据结构定义 ============

class TaskItem(BaseModel):
    """任务项"""
    title: str = Field(description="任务标题")
    description: str = Field(default="", description="任务描述（可选）")
    estimated_hours: float = Field(description="预估时间（小时）")
    order: int = Field(description="任务顺序")

    @field_validator('estimated_hours')
    @classmethod
    def validate_hours(cls, v):
        if v <= 0:
            raise ValueError('预估时间必须大于0')
        return v


class StageItem(BaseModel):
    """阶段项"""
    name: str = Field(description="阶段名称")
    order: int = Field(description="阶段顺序")
    description: str = Field(default="", description="阶段描述（可选）")
    tasks: list[TaskItem] = Field(description="该阶段的任务列表")

    @field_validator('tasks')
    @classmethod
    def validate_tasks(cls, v):
        if len(v) < 3 or len(v) > 8:
            raise ValueError('每个阶段的任务数量应在3-8个之间')
        return v


class PlanOutput(BaseModel):
    """规划输出"""
    stages: list[StageItem] = Field(description="规划的所有阶段")

    @field_validator('stages')
    @classmethod
    def validate_stages(cls, v):
        if len(v) < 2 or len(v) > 6:
            raise ValueError('阶段数量应在2-6个之间')
        return v


# ============ Prompt 模板 ============

SYSTEM_PROMPT = """
你是一个专业的目标规划助手，擅长将长期目标分解为可执行的短期任务。

你的任务：
1. 分析用户的目标和约束条件
2. 将目标分解为 3-5 个阶段
3. 每个阶段分解为具体的任务
4. 估算每个任务的时间（小时）
5. 确保任务之间的逻辑顺序合理
"""


def generate_prompt_template() -> ChatPromptTemplate:
    """
    生成 ChatPromptTemplate

    Returns:
        ChatPromptTemplate 对象
    """
    template = SYSTEM_PROMPT + """

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

{format_instructions}
"""
    return ChatPromptTemplate.from_template(template)


# ============ 链式处理器 ============

class PlanChain:
    """规划生成链"""

    def __init__(self, llm):
        """
        初始化链

        Args:
            llm: LangChain LLM 实例
        """
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=PlanOutput)
        self.prompt = generate_prompt_template()
        self.chain = self._build_chain()
        logger.info("规划链初始化成功")

    def _build_chain(self):
        """构建 LangChain 链"""
        chain = (
            {
                "goal_title": RunnablePassthrough(),
                "goal_description": RunnablePassthrough(),
                "deadline": RunnablePassthrough(),
                "available_hours": RunnablePassthrough(),
                "format_instructions": lambda _: self.parser.get_format_instructions()
            }
            | self.prompt
            | self.llm
            | self.parser
        )
        return chain

    def invoke(self, goal_title: str, goal_description: str, deadline: str, available_hours: int) -> PlanOutput:
        """
        执行链生成规划

        Args:
            goal_title: 目标标题
            goal_description: 目标描述
            deadline: 截止日期
            available_hours: 每天可用小时数

        Returns:
            PlanOutput 对象

        Raises:
            Exception: 链执行失败
        """
        return self.chain.invoke({
            "goal_title": goal_title,
            "goal_description": goal_description,
            "deadline": deadline if deadline else '未指定',
            "available_hours": available_hours
        })

    def to_dict(self, plan_output: PlanOutput) -> Dict[str, Any]:
        """
        将 PlanOutput 转换为字典

        Args:
            plan_output: PlanOutput 对象

        Returns:
            字典格式的规划数据
        """
        return {
            "stages": [
                {
                    "name": stage.name,
                    "order": stage.order,
                    "description": stage.description,
                    "tasks": [
                        {
                            "title": task.title,
                            "description": task.description,
                            "estimated_hours": task.estimated_hours,
                            "order": task.order
                        }
                        for task in stage.tasks
                    ]
                }
                for stage in plan_output.stages
            ]
        }


# ============ AI 服务 ============

class AIService:
    """AI 规划生成服务"""

    def __init__(self):
        """初始化 AI 客户端"""
        self.llm = None
        self.llm_operator = None
        self.plan_chain = None

        # 只有配置了 API Key 才初始化客户端
        if settings.LLM_MODEL_API_KEY:
            self._init_llm()
        else:
            logger.warning("未配置 LLM_MODEL_API_KEY，AI 服务将使用降级方案")

    def _init_llm(self):
        """初始化 LLM 客户端"""
        try:
            self.llm_operator = LLMOperator(
                model_name=settings.LLM_MODEL_NAME,
                api_key=settings.LLM_MODEL_API_KEY,
                base_url=settings.LLM_MODEL_BASE_URL,
                api_type=settings.LLM_MODEL_API_TYPE
            )
            self.llm = self.llm_operator.get_llm()
            self.plan_chain = PlanChain(self.llm)
            logger.info(f"AI 服务初始化成功，模型: {settings.LLM_MODEL_NAME}")
        except Exception as e:
            logger.error(f"AI 服务初始化失败: {e}")
            self.llm = None
            self.llm_operator = None
            self.plan_chain = None

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
        # 如果未配置 API Key 或链未初始化，使用降级方案
        if not self.plan_chain:
            logger.info("使用降级方案生成规划")
            return self._get_fallback_plan(goal_title)

        try:
            # 调用 AI API
            logger.info(f"调用 AI 生成规划，目标：{goal_title}")

            # 执行链生成规划
            plan_output = self.plan_chain.invoke(
                goal_title=goal_title,
                goal_description=goal_description,
                deadline=deadline,
                available_hours=available_hours
            )

            logger.info(f"规划生成成功，包含 {len(plan_output.stages)} 个阶段")

            # 转换为字典格式
            return self.plan_chain.to_dict(plan_output)

        except ValueError as e:
            logger.error(f"规划数据验证失败：{e}")
            # 使用降级方案
            logger.info("使用降级方案生成规划")
            return self._get_fallback_plan(goal_title)

        except Exception as e:
            logger.error(f"AI 调用失败：{e}", exc_info=True)
            # 使用降级方案
            logger.info("使用降级方案生成规划")
            return self._get_fallback_plan(goal_title)

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
