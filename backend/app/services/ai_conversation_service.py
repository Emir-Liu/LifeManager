"""
AI Conversation Service
AI 对话服务 - 负责与 AI 模型交互，管理 Prompt 和上下文
"""
import json
from datetime import datetime
from typing import Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.models.conversation import Conversation, ConversationMessage
from app.schemas.conversation import Action, ActionStatus, MessageCreate, ConversationType, MessageRole
from app.services.conversation_service import ConversationService
from app.utils.llm_operator import LLMOperator


class AIConversationService:
    """AI 对话服务"""

    def __init__(self, db: AsyncSession, llm_operator: Optional[LLMOperator] = None):
        self.db = db
        self.conversation_service = ConversationService(db)

        # 初始化 LLM
        if llm_operator:
            self.llm = llm_operator.get_llm()
        else:
            llm_operator = LLMOperator(
                model_name=settings.AI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_API_BASE,
                api_type="openai",
            )
            self.llm = llm_operator.get_llm()

    def _build_prompt(self, conversation_type: ConversationType, context: dict) -> str:
        """构建 Prompt 模板"""
        templates = {
            ConversationType.GOAL_PLANNING: self._get_goal_planning_prompt(context),
            ConversationType.SCHEDULE_PLANNING: self._get_schedule_planning_prompt(context),
            ConversationType.TASK_ADJUSTMENT: self._get_task_adjustment_prompt(context),
            ConversationType.GENERAL_CHAT: self._get_general_chat_prompt(context),
        }

        return templates.get(conversation_type, templates[ConversationType.GENERAL_CHAT])

    def _get_goal_planning_prompt(self, context: dict) -> str:
        """目标规划 Prompt 模板"""
        return f"""你是 LifeManager 的智能助手，帮助用户规划目标和任务。

当前对话类型：目标规划

你的职责：
1. 理解用户的目标描述
2. 询问必要的信息（如时间、难度、资源等）
3. 提供合理的目标分解建议
4. 生成可执行的任务计划

对话历史：
{context.get('conversation_history', '')}

用户时间偏好：
{context.get('time_preferences', '未设置')}

当前用户输入：
{{user_input}}

请以友好、专业的方式回应用户。如果需要创建目标或任务，请在回复中明确指出操作意图。
"""

    def _get_schedule_planning_prompt(self, context: dict) -> str:
        """日程规划 Prompt 模板"""
        return f"""你是 LifeManager 的智能助手，帮助用户规划日程。

当前对话类型：日程规划

你的职责：
1. 理解用户的日程需求
2. 考虑用户的时间偏好和已有日程
3. 提供合理的时间安排建议
4. 检测并解决时间冲突

用户已有日程：
{context.get('existing_events', '无')}

用户时间偏好：
{context.get('time_preferences', '未设置')}

当前用户输入：
{{user_input}}

请提供具体的时间安排建议。如果需要创建日程，请在回复中明确指出。
"""

    def _get_task_adjustment_prompt(self, context: dict) -> str:
        """任务调整 Prompt 模板"""
        return f"""你是 LifeManager 的智能助手，帮助用户调整任务。

当前对话类型：任务调整

你的职责：
1. 理解用户的调整需求
2. 检测调整后的影响
3. 提供合理的调整建议
4. 处理时间冲突

当前任务信息：
{context.get('task_info', '无')}

用户时间偏好：
{context.get('time_preferences', '未设置')}

当前用户输入：
{{user_input}}

请提供合理的调整建议。
"""

    def _get_general_chat_prompt(self, context: dict) -> str:
        """通用聊天 Prompt 模板"""
        return """你是 LifeManager 的智能助手。

你可以帮助用户：
- 制定目标和计划
- 管理任务和日程
- 提供时间管理建议

当前用户输入：
{{user_input}}

请以友好、专业的方式回应用户。
"""

    async def _extract_action(self, ai_response: str) -> Optional[dict]:
        """从 AI 响应中提取操作信息"""
        # 这里简化处理，实际可以使用更复杂的解析逻辑
        if "创建目标" in ai_response or "create_goal" in ai_response.lower():
            return {"action_type": Action.CREATE_GOAL, "description": ai_response[:500]}
        elif "创建任务" in ai_response or "create_task" in ai_response.lower():
            return {"action_type": Action.CREATE_TASK, "description": ai_response[:500]}
        elif "创建日程" in ai_response or "create_event" in ai_response.lower():
            return {"action_type": Action.CREATE_EVENT, "description": ai_response[:500]}
        return None

    async def _get_conversation_context(self, conversation: Conversation) -> dict:
        """获取对话上下文"""
        # 获取对话历史
        messages = await self.conversation_service.get_conversation_messages(
            conversation.id, conversation.user_id
        )

        # 格式化对话历史
        conversation_history = ""
        for msg in messages[-5:]:  # 只取最近 5 条消息
            role_name = "用户" if msg.role == MessageRole.USER else "AI"
            conversation_history += f"{role_name}: {msg.content}\n"

        # 获取用户时间偏好
        # TODO: 从数据库获取用户时间偏好
        time_preferences = "未设置"

        # 根据对话类型获取不同的上下文
        context = {
            "conversation_type": conversation.conversation_type,
            "conversation_history": conversation_history,
            "time_preferences": time_preferences,
        }

        if conversation.conversation_type == ConversationType.SCHEDULE_PLANNING:
            context["existing_events"] = "TODO: 获取用户已有日程"
        elif conversation.conversation_type == ConversationType.TASK_ADJUSTMENT:
            context["task_info"] = "TODO: 获取任务信息"

        return context

    async def process_message(
        self, conversation_id: int, user_id: int, user_input: str
    ) -> ConversationMessage:
        """处理用户消息并生成 AI 回复"""
        # 获取对话
        conversation = await self.conversation_service.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")

        # 添加用户消息
        user_message = await self.conversation_service.add_message(
            conversation_id,
            user_id,
            MessageCreate(
                role=MessageRole.USER,
                message_type="text",
                content=user_input,
            ),
        )

        # 获取对话上下文
        context = await self._get_conversation_context(conversation)

        # 构建 Prompt
        prompt = self._build_prompt(conversation.conversation_type, context).replace(
            "{{user_input}}", user_input
        )

        try:
            # 调用 LLM
            messages = [HumanMessage(content=prompt)]
            ai_response = await self.llm.ainvoke(messages)

            ai_content = ai_response.content

            # 记录 token 使用
            tokens_used = getattr(ai_response, "usage_metadata", {}).get("total_tokens", 0)

            # 添加 AI 回复消息
            ai_message = await self.conversation_service.add_message(
                conversation_id,
                user_id,
                MessageCreate(
                    role=MessageRole.ASSISTANT,
                    message_type="text",
                    content=ai_content,
                    model_used=settings.AI_MODEL,
                    tokens_used=tokens_used,
                ),
            )

            # 尝试提取操作
            action_data = await self._extract_action(ai_content)
            if action_data:
                await self.conversation_service.create_action(
                    message_id=ai_message.id,
                    conversation_id=conversation_id,
                    action_type=action_data["action_type"],
                    description=action_data["description"],
                )

            return ai_message

        except Exception as e:
            logger.error(f"AI 对话失败: {e}")
            raise
