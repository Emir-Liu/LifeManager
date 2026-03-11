"""
配置信息管理类
"""

import os
from dotenv import load_dotenv


class LLMConfig:
    """
    配置类
    """
    def __init__(self, config_path: str | None = None) -> None:
        # 加载.env系统环境变量
        if config_path is None:
            config_path = '.env'
        bool_load_env: bool = load_dotenv(dotenv_path=config_path)

        # 读取配置信息
        self.config_path: str = config_path

        self.model_name: str = os.getenv('LLM_MODEL_NAME', '')
        self.base_url: str = os.getenv('LLM_MODEL_BASE_URL', '')
        self.api_key: str = os.getenv('LLM_MODEL_API_KEY', '')
        self.api_type: str = os.getenv('LLM_MODEL_API_TYPE', 'openai')

    def show_config(self) -> None:
        """
        显示配置信息
        """
        for attr, value in self.__dict__.items():
            if not attr.startswith('_'):
                print(f"{attr}: {value}")


if __name__ == '__main__':
    llm_config: LLMConfig = LLMConfig()
    llm_config.show_config()
