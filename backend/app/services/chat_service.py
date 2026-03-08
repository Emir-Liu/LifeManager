"""
基础聊天服务 - 实现简单的对话功能
"""
import json
from typing import Dict, Any, List, AsyncIterator
from app.core.logger import logger
from app.core.config import settings
from app.utils.llm_operator import LLMOperator


class ChatService:
    """基础聊天服务"""

    def __init__(self):
        """初始化聊天服务"""
        self.llm_operator = None
        self._init_llm()

    def _init_llm(self):
        """初始化 LLM 客户端"""
        try:
            if settings.LLM_MODEL_API_KEY:
                self.llm_operator = LLMOperator(
                    model_name=settings.LLM_MODEL_NAME,
                    api_key=settings.LLM_MODEL_API_KEY,
                    base_url=settings.LLM_MODEL_BASE_URL,
                    api_type=settings.LLM_MODEL_API_TYPE
                )
                logger.info(f"聊天服务初始化成功，模型: {settings.LLM_MODEL_NAME}")
            else:
                logger.warning("未配置 LLM_MODEL_API_KEY，聊天服务将使用降级方案")
        except Exception as e:
            logger.error(f"聊天服务初始化失败: {e}")
            self.llm_operator = None

    def chat(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        发送消息并获取回复

        Args:
            user_message: 用户消息
            conversation_history: 对话历史记录（可选）

        Returns:
            AI 回复内容
        """
        # 如果未配置 LLM，使用降级方案
        if not self.llm_operator:
            logger.info("使用降级方案生成回复")
            return self._get_fallback_response(user_message)

        try:
            # 构建消息列表
            messages = []

            # 添加系统提示
            messages.append({
                "role": "system",
                "content": self._get_system_prompt()
            })

            # 添加历史对话（如果有）
            if conversation_history:
                for msg in conversation_history[-6:]:  # 只使用最近6条历史
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg.get('content', '')
                        })

            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })

            logger.info(f"调用 LLM，消息数: {len(messages)}")

            # 调用 LLM
            llm = self.llm_operator.get_llm()
            response = llm.invoke(messages)

            # 解析响应
            ai_response = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"LLM 回复成功，长度: {len(ai_response)}")

            return ai_response

        except Exception as e:
            logger.error(f"LLM 调用失败: {e}", exc_info=True)
            # 使用降级方案
            logger.info("使用降级方案生成回复")
            return self._get_fallback_response(user_message)

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是 LifeManager 的智能助手，一个专业的个人生活管理助手。

你的职责：
1. 帮助用户制定目标和规划
2. 提供任务管理建议
3. 回答用户关于时间管理和生产力的问题
4. 提供积极、有建设性的建议

沟通风格：
- 友好、专业、简洁
- 给出具体可行的建议
- 避免过于冗长的回答
- 鼓励用户行动

记住：
- 你是一个助手，不是心理咨询师
- 不要提供医疗、法律等专业建议
- 保持积极正面的态度"""

    def _get_fallback_response(self, user_message: str) -> str:
        """
        获取降级回复（当 LLM 不可用时）

        Args:
            user_message: 用户消息

        Returns:
            回复内容
        """
        # 简单的关键词匹配回复
        msg_lower = user_message.lower()

        if any(word in msg_lower for word in ['你好', 'hello', '嗨', 'hi']):
            return "你好！我是 LifeManager 的智能助手。有什么可以帮助你的吗？"

        elif any(word in msg_lower for word in ['目标', '计划', '规划']):
            return "制定目标很重要！建议你使用 SMART 原则：\n\n1. Specific（具体的）：目标要明确\n2. Measurable（可衡量的）：有明确标准\n3. Achievable（可实现的）：符合实际\n4. Relevant（相关的）：与你的价值观一致\n5. Time-bound（有时限的）：设定截止日期\n\n需要我帮你分解一个具体的目标吗？"

        elif any(word in msg_lower for word in ['任务', 'todo', '待办']):
            return "任务管理的小技巧：\n\n1. 使用艾森豪威尔矩阵分类任务\n2. 每天优先处理重要紧急的任务\n3. 将大任务分解为小任务\n4. 设定明确的截止日期\n5. 定期回顾和调整任务\n\n你目前有哪些任务需要处理？"

        elif any(word in msg_lower for word in ['时间', '管理', '效率']):
            return "提高时间管理效率的方法：\n\n1. 使用番茄工作法：工作25分钟，休息5分钟\n2. 每天早上列出最重要的3件事\n3. 设定固定的工作时间\n4. 学会说\"不\"，避免过度承诺\n5. 定期回顾时间使用情况\n\n需要我帮你制定时间计划吗？"

        elif any(word in msg_lower for word in ['谢谢', '感谢']):
            return "不客气！能帮到你很开心。还有其他问题吗？"

        elif '?' in msg_lower or '？' in msg_lower or '吗' in msg_lower or any(word in msg_lower for word in ['怎么', '如何', '什么']):
            return "这是个好问题！作为 LifeManager 的助手，我可以帮助你：\n\n📋 **任务管理**\n- 制定和追踪任务\n- 设置优先级和截止日期\n\n🎯 **目标规划**\n- 分解长期目标\n- 制定阶段性计划\n\n📅 **日程安排**\n- 时间线规划\n- 日程优化建议\n\n📊 **统计分析**\n- 进度跟踪\n- 效率分析\n\n请告诉我你需要哪方面的帮助？"

        else:
            return "我收到了你的消息！作为 LifeManager 的智能助手，我可以帮助你：\n\n📋 **任务管理** - 制定和追踪任务\n🎯 **目标规划** - 分解长期目标\n📅 **日程安排** - 时间线规划\n📊 **统计分析** - 进度跟踪分析\n\n请问需要我帮你做什么？"

    async def chat_stream(self, user_message: str, conversation_history: List[Dict] = None) -> AsyncIterator[str]:
        """
        流式发送消息并获取回复

        Args:
            user_message: 用户消息
            conversation_history: 对话历史记录(可选)

        Yields:
            AI 回复的每个 chunk
        """
        # 如果未配置 LLM，使用降级方案
        if not self.llm_operator:
            logger.info("使用降级方案生成回复")
            fallback_response = self._get_fallback_response(user_message)
            # 流式输出降级回复
            for char in fallback_response:
                yield char
            return

        try:
            # 构建消息列表
            messages = []

            # 添加系统提示
            messages.append({
                "role": "system",
                "content": self._get_system_prompt()
            })

            # 添加历史对话（如果有）
            if conversation_history:
                for msg in conversation_history[-6:]:  # 只使用最近6条历史
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg.get('content', '')
                        })

            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })

            logger.info(f"调用 LLM 流式接口，消息数: {len(messages)}")

            # 调用 LLM 流式接口
            llm = self.llm_operator.get_llm()
            stream = llm.stream(messages)

            # 流式输出
            for chunk in stream:
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:  # 只返回非空内容
                    yield content

            logger.info(f"LLM 流式回复完成")

        except Exception as e:
            logger.error(f"LLM 流式调用失败: {e}", exc_info=True)
            # 使用降级方案
            logger.info("使用降级方案生成回复")
            fallback_response = self._get_fallback_response(user_message)
            for char in fallback_response:
                yield char


# 全局实例
chat_service = ChatService()
