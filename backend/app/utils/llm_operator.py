"""
大模型相关操作类
"""

from langchain_core.messages.ai import AIMessage
from langchain_core.exceptions import OutputParserException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.logger import logger


class LLMOperator:
    def __init__(self, model_name: str, api_key: str, base_url: str, api_type: str) -> None:
        """
        初始化大模型操作类

        Args:
            model_name: 模型名称
            api_key: API 密钥
            base_url: API 地址
            api_type: API 类型 (openai/bailian)
        """
        low_model_name = model_name.lower().strip()

        if api_type == 'openai':
            from langchain_openai import ChatOpenAI
            if 'qwen3' in low_model_name:
                # vllm 本地部署的 qwen3 模型需要使用 extra_body 传递 chat_template_kwargs
                llm: ChatOpenAI = ChatOpenAI(
                    model=model_name,
                    base_url=base_url,
                    api_key=api_key,
                    streaming=False,
                    max_retries=5,
                    temperature=0.7,
                    extra_body={
                        "chat_template_kwargs": {"enable_thinking": False},
                    }
                )
            else:
                llm: ChatOpenAI = ChatOpenAI(
                    model=model_name,
                    base_url=base_url,
                    api_key=api_key,
                    streaming=False,
                    max_retries=5,
                    temperature=0.7,
                )

            self.model: ChatOpenAI = llm
        elif api_type == 'bailian':
            from langchain_openai import ChatOpenAI
            if 'qwen3' in low_model_name:
                # 千问平台的 qwen3 模型
                llm: ChatOpenAI = ChatOpenAI(
                    model=model_name,
                    base_url=base_url,
                    api_key=api_key,
                    streaming=False,
                    max_retries=5,
                    temperature=0.7,
                    extra_body={
                        "enable_thinking": False,
                    }
                )
            else:
                llm: ChatOpenAI = ChatOpenAI(
                    model=model_name,
                    base_url=base_url,
                    api_key=api_key,
                    streaming=False,
                    max_retries=5,
                    temperature=0.7,
                )
            self.model: ChatOpenAI = llm
        else:
            logger.error(f'不支持当前格式的api_type: {api_type}')
            raise ValueError(f'不支持的 API 类型: {api_type}')

        logger.info(f"LLMOperator 初始化成功，模型: {model_name}, API 类型: {api_type}")

    def get_llm(self):
        """获取 LLM 实例"""
        return self.model
