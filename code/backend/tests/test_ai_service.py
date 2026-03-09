"""
AI 服务单元测试
"""
import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService, generate_prompt


class TestGeneratePrompt:
    """测试 Prompt 生成函数"""

    def test_generate_prompt_basic(self):
        """测试基本 Prompt 生成"""
        prompt = generate_prompt(
            goal_title="学习Python",
            goal_description="在3个月内掌握Python",
            deadline="2026-04-30",
            available_hours=2
        )

        assert "学习Python" in prompt
        assert "在3个月内掌握Python" in prompt
        assert "2026-04-30" in prompt
        assert "2" in prompt
        assert "JSON 格式" in prompt

    def test_generate_prompt_without_deadline(self):
        """测试无截止日期的 Prompt 生成"""
        prompt = generate_prompt(
            goal_title="健康生活",
            goal_description="养成健康习惯",
            deadline="",
            available_hours=1
        )

        assert "未指定" in prompt

    def test_generate_prompt_json_format(self):
        """测试 Prompt 包含正确的 JSON 格式说明"""
        prompt = generate_prompt("测试", "测试描述", "2026-12-31", 3)

        assert '"stages"' in prompt
        assert '"name"' in prompt
        assert '"tasks"' in prompt
        assert '"title"' in prompt
        assert '"estimated_hours"' in prompt


class TestAIService:
    """测试 AI 服务类"""

    def test_init_without_api_key(self):
        """测试无 API Key 初始化"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.LLM_MODEL_API_KEY = ""
            service = AIService()

            assert service.llm is None
            assert service.llm_operator is None

    @patch('app.services.ai_service.settings')
    @patch('app.services.ai_service.LLMOperator')
    def test_init_with_api_key(self, mock_llm_operator, mock_settings):
        """测试有 API Key 初始化"""
        mock_settings.LLM_MODEL_API_KEY = "test-key"
        mock_settings.LLM_MODEL_NAME = "test-model"
        mock_settings.LLM_MODEL_BASE_URL = "http://test.com"
        mock_settings.LLM_MODEL_API_TYPE = "openai"

        mock_operator_instance = Mock()
        mock_llm_operator.return_value = mock_operator_instance
        mock_operator_instance.get_llm.return_value = Mock()

        service = AIService()

        assert service.llm is not None
        assert service.llm_operator is not None

    def test_get_fallback_plan(self):
        """测试降级方案"""
        service = AIService()
        plan = service._get_fallback_plan("学习Python")

        assert "stages" in plan
        assert len(plan["stages"]) == 3

        # 检查阶段结构
        for stage in plan["stages"]:
            assert "name" in stage
            assert "tasks" in stage
            assert len(stage["tasks"]) > 0

            # 检查任务结构
            for task in stage["tasks"]:
                assert "title" in task
                assert "estimated_hours" in task

    def test_validate_plan_data_valid(self):
        """测试有效的规划数据验证"""
        service = AIService()
        plan_data = {
            "stages": [
                {
                    "name": "阶段1",
                    "tasks": [
                        {
                            "title": "任务1",
                            "estimated_hours": 2.0
                        }
                    ]
                }
            ]
        }

        # 不应该抛出异常
        service._validate_plan_data(plan_data)

    def test_validate_plan_data_missing_stages(self):
        """测试缺少 stages 字段"""
        service = AIService()
        plan_data = {}

        with pytest.raises(ValueError, match="缺少 stages 字段"):
            service._validate_plan_data(plan_data)

    def test_validate_plan_data_empty_stages(self):
        """测试空的 stages"""
        service = AIService()
        plan_data = {
            "stages": []
        }

        with pytest.raises(ValueError, match="必须是非空列表"):
            service._validate_plan_data(plan_data)

    def test_validate_plan_data_too_many_stages(self):
        """测试阶段数量过多"""
        service = AIService()
        plan_data = {
            "stages": [
                {"name": f"阶段{i}", "tasks": []}
                for i in range(7)  # 超过6个
            ]
        }

        with pytest.raises(ValueError, match="阶段数量应在 2-6 个之间"):
            service._validate_plan_data(plan_data)

    def test_validate_plan_data_missing_task_fields(self):
        """测试任务缺少必要字段"""
        service = AIService()
        plan_data = {
            "stages": [
                {
                    "name": "阶段1",
                    "tasks": [
                        {"title": "任务1"}  # 缺少 estimated_hours
                    ]
                }
            ]
        }

        with pytest.raises(ValueError, match="缺少必要字段"):
            service._validate_plan_data(plan_data)

    def test_validate_plan_data_invalid_hours(self):
        """测试无效的工时"""
        service = AIService()
        plan_data = {
            "stages": [
                {
                    "name": "阶段1",
                    "tasks": [
                        {
                            "title": "任务1",
                            "estimated_hours": "invalid"  # 不是数字
                        }
                    ]
                }
            ]
        }

        with pytest.raises(ValueError, match="estimated_hours 必须是数字"):
            service._validate_plan_data(plan_data)

    @patch('app.services.ai_service.settings')
    def test_generate_plan_without_llm(self, mock_settings):
        """测试无 LLM 时使用降级方案"""
        mock_settings.LLM_MODEL_API_KEY = ""

        service = AIService()
        plan = service.generate_plan(
            goal_title="学习Python",
            goal_description="掌握Python基础",
            deadline="2026-04-30",
            available_hours=2
        )

        assert "stages" in plan
        assert len(plan["stages"]) == 3

    @patch('app.services.ai_service.settings')
    @patch('app.services.ai_service.LLMOperator')
    def test_generate_plan_with_llm(self, mock_llm_operator, mock_settings):
        """测试有 LLM 时生成规划"""
        mock_settings.LLM_MODEL_API_KEY = "test-key"
        mock_settings.LLM_MODEL_NAME = "test-model"
        mock_settings.LLM_MODEL_BASE_URL = "http://test.com"
        mock_settings.LLM_MODEL_API_TYPE = "openai"

        # Mock LLM 响应
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = '{"stages": [{"name": "阶段1", "tasks": [{"title": "任务1", "estimated_hours": 2.0}]}]}'

        mock_operator_instance = Mock()
        mock_llm_operator.return_value = mock_operator_instance
        mock_operator_instance.get_llm.return_value = mock_llm

        service = AIService()
        plan = service.generate_plan(
            goal_title="学习Python",
            goal_description="掌握Python基础",
            deadline="2026-04-30",
            available_hours=2
        )

        assert "stages" in plan
        assert len(plan["stages"]) == 1
        mock_llm.invoke.assert_called_once()
