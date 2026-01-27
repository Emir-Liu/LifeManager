"""
大模型相关操作类
"""

from langchain_core.messages.ai import AIMessage
from langchain_core.exceptions import OutputParserException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.config import Config
from app.utils.logger_operator import LoguruOperator

logger = LoguruOperator().init_app('llm_operator')


class LLMOperator():
    def __init__(self, model_name: str, api_key: str, base_url: str, api_type: str) -> None:
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
        return self.model



if __name__ == '__main__':
    config: Config = Config()

    llm = LLMOperator(
        model_name=config.llm_model_name, 
        api_key=config.llm_model_api_key, 
        base_url=config.llm_model_base_url,
        api_type=config.llm_model_api_type
    ).get_llm()

    ret_str: AIMessage = llm.invoke(
        input='你是谁', 
        # stream=True
    )

    print(ret_str)