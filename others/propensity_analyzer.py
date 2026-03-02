"""
投诉倾向识别分析器
分析对话中的投诉倾向，包括语气、情绪、满意度、重复提问、威胁性语言等维度
"""

import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from config.config import Config
from app.utils.llm_operator import LLMOperator
from app.utils.logger_operator import LoguruOperator
from app.core.db.crud.crud_cip_rules import get_cip_rules
from app.core.cip_analyzer.PropensityAnalyzer.base_propensity_analyzer import BasePropensityAnalyzer
from app.core.cip_analyzer.PropensityAnalyzer.propensity_model import (
    PropensityAnalysisResult,
    ClassificationItem,
    CIPAnalysisResult
)
from app.core.cip_analyzer.PropensityAnalyzer.propensity_prompt import CIP_ANALYZER_PROMPT

logger = LoguruOperator.init_app('cip_propensity')

class PropensityAnalyzer(BasePropensityAnalyzer):
    """投诉倾向识别分析器"""

    def __init__(
        self, 
        llm_model_name, 
        llm_model_api_key, 
        llm_model_base_url, 
        llm_model_api_type,
        slice_config = None,
    ):
        """初始化分析器

        Args:
            model_name: 模型名称
            api_key: API密钥
            base_url: 基础URL
            api_type: API类型
            max_tokens_per_page: 每页最大token数

        Returns:
            None
        """
        self.llm = LLMOperator(
            model_name=llm_model_name,
            api_key=llm_model_api_key,
            base_url=llm_model_base_url,
            api_type=llm_model_api_type
        ).get_llm()

        self.parser = PydanticOutputParser(pydantic_object=CIPAnalysisResult)
        self.prompt = PromptTemplate(
            template=CIP_ANALYZER_PROMPT,
            input_variables=["conversation_text", "classification_rules"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | self.parser

        # # 加载投诉分类规则
        # self.classification_rules = self._load_classification_rules()
        # logger.info(f"成功加载投诉分类规则，共 {len(self.classification_rules)} 条")

    def _load_classification_rules(self) -> List[Dict[str, Any]]:
        """从数据库加载投诉分类规则

        Returns:
            规则列表
        """
        try:
            rules = get_cip_rules()
            # logger.info(f"成功加载投诉分类规则，共 {len(rules)} 条:\n{rules}")
            # logger.debug(f"投诉分类规则: {json.dumps(rules, ensure_ascii=False, indent=2)}")
            return rules
        except Exception as e:
            logger.error(f"加载投诉分类规则失败: {e}")
            return []

    def _format_classification_rules_list(self, rules) -> str:
        """格式化分类规则为Prompt字符串
        """
        if not rules:
            return "暂无分类规则"

        # 按大类分组
        rules_by_category: Dict[str, List[Dict]] = {}
        for rule in rules:
            category = rule.get('category', '未知')
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(rule)

        # logger.info(f"rules_by_category: {json.dumps(rules_by_category, ensure_ascii=False, indent=2)}")

        # 格式化输出
        formatted_rules = []
        for category, rules in rules_by_category.items():
            category_id = rules[0].get('category_id', '')
            formatted_rules.append(f"\n投诉类型大类：{category} (投诉类型大类ID: {category_id})")
            for rule in rules:
                sub_category = rule.get('sub_category', '')
                manifestation = rule.get('manifestation', '')
                scenario = rule.get('scenario_description', '')
                key_phrases = rule.get('key_phrases', '')
                sub_category_id = rule.get('sub_category_id', '')

                # 解析key_phrases JSON
                if isinstance(key_phrases, str):
                    try:
                        key_phrases = json.loads(key_phrases)
                    except:
                        key_phrases = []

                rule_text = f"  - 投诉类型小类：{sub_category} （投诉类型小类ID：{sub_category_id}）\n"
                if manifestation:
                    rule_text += f"    具体表现: {manifestation}\n"
                if scenario:
                    rule_text += f"    典型场景: {scenario}\n"
                if key_phrases:
                    rule_text += f"    关键词: {', '.join(key_phrases)}\n"

                formatted_rules.append(rule_text)

        return "\n".join(formatted_rules)

    def _format_classification_rules(self) -> str:
        """格式化分类规则为Prompt字符串

        Returns:
            格式化后的规则字符串
        """
        if not self.classification_rules:
            return "暂无分类规则"

        # 按大类分组
        rules_by_category: Dict[str, List[Dict]] = {}
        for rule in self.classification_rules:
            category = rule.get('category', '未知')
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(rule)

        # 格式化输出
        formatted_rules = []
        for category, rules in rules_by_category.items():
            category_id = rules[0].get('category_id', '')
            formatted_rules.append(f"\n投诉类型大类：{category} (投诉类型大类ID: {category_id})")
            for rule in rules:
                sub_category = rule.get('sub_category', '')
                manifestation = rule.get('manifestation', '')
                scenario = rule.get('scenario_description', '')
                key_phrases = rule.get('key_phrases', '')
                sub_category_id = rule.get('sub_category_id', '')

                # 解析key_phrases JSON
                if isinstance(key_phrases, str):
                    try:
                        key_phrases = json.loads(key_phrases)
                    except:
                        key_phrases = []

                rule_text = f"  - 投诉类型小类：{sub_category} （投诉类型小类ID：{sub_category_id}）\n"
                if manifestation:
                    rule_text += f"    具体表现: {manifestation}\n"
                if scenario:
                    rule_text += f"    典型场景: {scenario}\n"
                if key_phrases:
                    rule_text += f"    关键词: {', '.join(key_phrases)}\n"

                formatted_rules.append(rule_text)

        return "\n".join(formatted_rules)

    def _format_conversation_text(self, conversation_json: Dict[str, Any]) -> str:
        """格式化对话文本为Prompt字符串

        Args:
            conversation_json: 对话JSON数据

        Returns:
            格式化后的对话字符串
        """

        # 这个字段是否一致？

        # transcripts = conversation_json.get('transcripts', [])
        # if transcripts:
        #     return ""

        # logger.info(f'conversation_json aaa: {conversation_json}')

        transcripts = []

        converation = conversation_json.get('conversation', [])
        if converation:
            transcripts = converation
        else:
            transcripts = conversation_json.get('transcripts', [])
        if not transcripts:
            return ""

        # logger.info(f'transcripts: {transcripts}')
        # if not transcripts and not converations:
        #     return ""

        formatted = []
        for item in transcripts:
            turn_id = item.get('turn_id', '')
            speaker = item.get('speaker', '')
            speaker_id = item.get('speaker_id', '')
            text = item.get('text', '')

            formatted.append(f"[轮次{turn_id}] {speaker}(ID:{speaker_id}): {text}")

        return "\n".join(formatted)

    def analyze(
        self, 
        conversation_json: Dict[str, Any], 
        enable_classification: bool = True, 
        rules = []
    ) -> Dict[str, Any]:
        """分析对话的投诉倾向

        Args:
            conversation_json: 对话JSON数据
            enable_classification: 是否启用投诉分类（默认true）

        Returns:
            分析结果字典:
            {
                'propensity_analysis': {
                    'propensity_level': str,  # 倾向等级
                    'confidence': float,  # 置信度(0-1)
                    'emotion_analysis': {...},  # 情绪分析
                    'tone_analysis': str,  # 语气分析
                    'satisfaction': str,  # 满意度
                    'repeat_question_count': int,  # 重复提问次数
                    'has_threatening_language': bool,  # 是否有威胁性语言
                    'evidence_chain': [...],  # 证据链
                    'suggested_action': str,  # 建议动作
                    'reasoning': str  # 推理过程
                },
                'classification': [...],  # 分类结果列表
            }
        """
        try:
            # 格式化输入
            conversation_text = self._format_conversation_text(conversation_json)

            logger.info(f"开始CIP分析，对话内容 {len(conversation_text)}: \n{conversation_text}")

            # 加载投诉分类规则
            if rules:
                classification_rules_text = self._format_classification_rules_list(rules)
                logger.info(f'classification_rules_text: {classification_rules_text}')
            else:
                self.classification_rules = self._load_classification_rules()
                logger.info(f"成功加载投诉分类规则，共 {len(self.classification_rules)} 条")
                classification_rules_text = self._format_classification_rules()
                logger.info(f'classification_rules_text: {classification_rules_text}')

            # 调用LLM
            result = self.chain.invoke({
                "conversation_text": conversation_text,
                "classification_rules": classification_rules_text
            })

            logger.info(f"CIP分析结果: {result}")

            # # 应用业务规则，这部分直接通过大模型实现
            # result = self._apply_business_rules(result)

            # 转换为字典
            result_dict = result.model_dump()

            logger.info(f"CIP分析完成: 倾向等级={result.propensity_analysis.propensity_level}, "
                       f"置信度={result.propensity_analysis.confidence:.2f}, "
                       f"情绪指标={result.propensity_analysis.emotion_analysis.emotion_score}, "
                       f"分类数量={len(result.classification)}")

            return result_dict

        except Exception as e:
            logger.error(f"CIP分析失败: {e}")
            raise


if __name__ == '__main__':

    from app.utils.time_operator import Timer

    with Timer() as t:
        # 测试代码
        config = Config()
        # analyzer = PropensityAnalyzer(config)

        analyzer = PropensityAnalyzer(
            llm_model_name=config.llm_model_name,
            llm_model_api_key=config.llm_model_api_key,
            llm_model_base_url=config.llm_model_base_url,
            llm_model_api_type=config.llm_model_api_type,
            max_tokens_per_page=1024,
        )

        # import json
        # long_conversation_json = {}
        # long_conversation_path = '../others/cip_data/long_conversation.json'
        # with open(long_conversation_path, 'r', encoding='utf-8') as f:
        #     long_conversation_json = json.load(f)

        # 测试对话数据
        long_conversation_json = {
            "transcripts": [
                {"turn_id": "1", "speaker": "SPEAKER_00", "speaker_id": "SPEAKER_00", "text": "你们这服务态度太差了！"},
                {"turn_id": "2", "speaker": "SPEAKER_01", "speaker_id": "SPEAKER_01", "text": "请问有什么可以帮助您的？"},
                {"turn_id": "3", "speaker": "SPEAKER_00", "speaker_id": "SPEAKER_00", "text": "我要投诉你们！态度太差了！"},
            ]
        }

        result = analyzer.analyze(long_conversation_json)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f'耗时: {t.get_elapsed_time()}')
    print(f'开始时间: {t.get_start_time_str()}')
    print(f'结束时间: {t.get_end_time_str()}')