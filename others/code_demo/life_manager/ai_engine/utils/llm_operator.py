"""
大模型相关操作类
"""

from langchain_core.messages.ai import AIMessage
from langchain_core.exceptions import OutputParserException

from ai_engine.config.config import LLMConfig


class LLMOperator:
    """LLM操作类"""
    
    def __init__(self, llm_config: LLMConfig) -> None:
        """初始化LLM操作类
        
        Args:
            llm_config: LLM配置对象
        """
        model_name = llm_config.model_name
        api_key = llm_config.api_key
        base_url = llm_config.base_url
        api_type = llm_config.api_type
        low_model_name = model_name.lower().strip()
        
        if api_type == 'openai':
            from langchain_openai import ChatOpenAI
            if 'qwen3' in low_model_name:
                llm: ChatOpenAI = ChatOpenAI(
                    model=model_name,
                    base_url=base_url,
                    api_key=api_key,
                    streaming=False,
                    max_retries=5,
                    extra_body={
                        # 下面是vllm本地部署的配置
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
                )
            self.model: ChatOpenAI = llm
            
        elif api_type == 'bailian':
            from langchain_openai import ChatOpenAI
            if 'qwen3' in low_model_name:
                llm: ChatOpenAI = ChatOpenAI(
                    model=model_name,
                    base_url=base_url,
                    api_key=api_key,
                    streaming=False,
                    max_retries=5,
                    extra_body={
                        # 下面是使用千问平台的配置
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
                )
            self.model: ChatOpenAI = llm
        else:
            print(f'不支持当前格式的api_type: {api_type}')

    def get_llm(self):
        """获取LLM实例"""
        return self.model
    
    def chat(self, user_input: str, system_prompt: str = None) -> AIMessage:
        """非流式对话
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词(可选)
            
        Returns:
            AI响应消息
        """
        if system_prompt:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            return self.model.invoke(messages)
        else:
            return self.model.invoke(user_input)
    
    def stream_chat(self, user_input: str, system_prompt: str = None):
        """流式对话
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词(可选)
            
        Yields:
            流式响应内容
        """
        if system_prompt:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            stream = self.model.stream(messages)
        else:
            stream = self.model.stream(user_input)
        
        for chunk in stream:
            yield chunk.content


if __name__ == '__main__':
    llm_config: LLMConfig = LLMConfig()

    llm = LLMOperator(
        llm_config
    ).get_llm()

    # 非流式调用
    ret_str: AIMessage = llm.invoke(
        input='你是谁'
    )
    print(f"非流式响应: {ret_str}")

    # 流式调用
    print("\n流式响应:")
    llm_operator = LLMOperator(llm_config)
    for chunk in llm_operator.stream_chat('介绍一下你自己'):
        print(chunk, end='', flush=True)
    print()
