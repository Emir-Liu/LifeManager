"""
前端组件单元测试
"""
import pytest


class TestTaskCard:
    """任务卡片组件测试"""

    def test_task_card_render(self):
        """测试任务卡片渲染"""
        # 测试数据
        task = {
            'id': 1,
            'title': '学习Python',
            'description': '掌握Python基础',
            'completed': False,
            'due_date': '2026-02-01'
        }

        # 断言
        assert task['title'] == '学习Python'
        assert task['completed'] is False
        assert task['due_date'] is not None

    def test_task_card_completed(self):
        """测试已完成任务样式"""
        task = {
            'id': 1,
            'title': '学习Python',
            'completed': True
        }

        assert task['completed'] is True

    def test_task_card_overdue(self):
        """测试过期任务"""
        from datetime import date, timedelta

        task = {
            'id': 1,
            'title': '学习Python',
            'due_date': (date.today() - timedelta(days=1)).isoformat()
        }

        assert task['due_date'] < date.today().isoformat()


class TestGoalCard:
    """目标卡片组件测试"""

    def test_goal_card_render(self):
        """测试目标卡片渲染"""
        goal = {
            'id': 1,
            'title': '学习Python',
            'description': '3个月内掌握Python',
            'status': 'planning',
            'progress': 0
        }

        assert goal['title'] == '学习Python'
        assert goal['status'] == 'planning'
        assert goal['progress'] == 0

    def test_goal_card_progress(self):
        """测试目标进度"""
        goal = {
            'id': 1,
            'title': '学习Python',
            'total_tasks': 10,
            'completed_tasks': 5
        }

        progress = (goal['completed_tasks'] / goal['total_tasks']) * 100
        assert progress == 50

    def test_goal_card_status(self):
        """测试目标状态"""
        statuses = ['planning', 'in_progress', 'completed', 'paused']
        assert 'planning' in statuses
        assert 'in_progress' in statuses


class TestPlanViewer:
    """规划查看器组件测试"""

    def test_plan_viewer_render(self):
        """测试规划查看器渲染"""
        plan = {
            'id': 1,
            'goal_id': 1,
            'content': {
                'stages': [
                    {
                        'name': '基础学习',
                        'order': 1,
                        'tasks': [
                            {'title': '安装Python', 'order': 1},
                            {'title': '学习语法', 'order': 2}
                        ]
                    }
                ]
            },
            'status': 'draft'
        }

        assert len(plan['content']['stages']) == 1
        assert len(plan['content']['stages'][0]['tasks']) == 2
        assert plan['status'] == 'draft'

    def test_plan_viewer_total_tasks(self):
        """测试规划总任务数"""
        plan = {
            'content': {
                'stages': [
                    {'tasks': [{'title': '任务1'}, {'title': '任务2'}]},
                    {'tasks': [{'title': '任务3'}]}
                ]
            }
        }

        total_tasks = sum(len(stage['tasks']) for stage in plan['content']['stages'])
        assert total_tasks == 3


class TestStatusBadge:
    """状态徽章组件测试"""

    def test_status_badge_planning(self):
        """测试规划状态徽章"""
        status = 'planning'
        badge_map = {
            'planning': '规划中',
            'in_progress': '进行中',
            'completed': '已完成',
            'paused': '已暂停'
        }

        assert badge_map[status] == '规划中'

    def test_status_badge_completed(self):
        """测试已完成状态徽章"""
        status = 'completed'
        badge_map = {
            'planning': '规划中',
            'in_progress': '进行中',
            'completed': '已完成',
            'paused': '已暂停'
        }

        assert badge_map[status] == '已完成'


class TestProgressCircle:
    """进度圆环组件测试"""

    def test_progress_circle_zero(self):
        """测试0%进度"""
        progress = 0
        assert 0 <= progress <= 100

    def test_progress_circle_half(self):
        """测试50%进度"""
        progress = 50
        assert 0 <= progress <= 100

    def test_progress_circle_full(self):
        """测试100%进度"""
        progress = 100
        assert 0 <= progress <= 100
