
from typing import List
from pydantic import BaseModel, Field

# 投诉倾向等级枚举
class PropensityLevel(str):
    """投诉倾向等级"""
    NONE = "无倾向"
    LOW = "低度疑虑"
    MEDIUM = "中度不满"
    HIGH = "高度风险"


# 证据链项
class EvidenceItem(BaseModel):
    """证据链项"""
    turn_id: str = Field(description="对话轮次ID")
    speaker: str = Field(description="说话人（客户/服务人员）")
    text: str = Field(description="关键话术原文")
    reason: str = Field(description="该话术体现的倾向原因")


# 情绪分析结果
class EmotionAnalysis(BaseModel):
    """情绪分析结果"""
    emotion_score: int = Field(description="情绪指标评分(0-100分，分数越高负面情绪越强)", ge=0, le=100)
    emotion_type: str = Field(description="情绪类型（愤怒/失望/焦虑/不满/平静等）")
    emotion_intensity: str = Field(description="情绪强度（轻微/中等/强烈）")


# 投诉倾向分析结果
class PropensityAnalysisResult(BaseModel):
    """投诉倾向分析结果"""
    propensity_level: str = Field(description="倾向等级（无倾向/低度疑虑/中度不满/高度风险）")
    confidence: float = Field(description="置信度(0.0-1.0)", ge=0.0, le=1.0)
    emotion_analysis: EmotionAnalysis = Field(description="情绪分析结果")
    tone_analysis: str = Field(description="语气分析（客户语气是否生硬、激动、不满等）")
    satisfaction: str = Field(description="满意度评估（对服务人员答疑的满意程度）")
    repeat_question_count: int = Field(description="重复提问次数", ge=0)
    has_threatening_language: bool = Field(description="是否存在威胁性语言（投诉、举报、曝光等）")
    evidence_chain: List[EvidenceItem] = Field(description="证据链：关键话术原文和轮次ID")
    suggested_action: str = Field(description="建议动作（人工复核、经理回访、标记风险等）")
    reasoning: str = Field(description="分析推理过程")


# 投诉分类结果项（支持多分类）
class ClassificationItem(BaseModel):
    """投诉分类结果项"""
    category: str = Field(description="投诉大类")
    sub_category: str = Field(description="投诉小类")
    category_id: str = Field(description="投诉大类ID")
    sub_category_id: str = Field(description="投诉小类ID")
    confidence: float = Field(description="分类置信度(0.0-1.0)", ge=0.0, le=1.0)
    classification_basis: str = Field(description="分类依据：引用对话文本并说明分类理由")


# 完整的CIP分析结果（倾向识别+分类）
class CIPAnalysisResult(BaseModel):
    """完整的CIP分析结果（倾向识别+分类）"""
    propensity_analysis: PropensityAnalysisResult = Field(description="投诉倾向分析结果")
    classification: List[ClassificationItem] = Field(description="投诉分类结果列表（支持多分类）,如果没有分类规则，则返回空列表")

