"""
数据库集成测试
"""
import pytest
from sqlalchemy.orm import Session
from app.models import User, Goal, Plan, Task


class TestDatabaseOperations:
    """数据库操作测试"""

    def test_user_crud(self, db: Session):
        """测试用户增删改查"""
        # 创建
        user = User(
            username="dbtest",
            password_hash="hashed_password",
            email="dbtest@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.username == "dbtest"

        # 读取
        fetched_user = db.query(User).filter(User.username == "dbtest").first()
        assert fetched_user is not None
        assert fetched_user.email == "dbtest@example.com"

        # 更新
        fetched_user.email = "updated@example.com"
        db.commit()
        db.refresh(fetched_user)
        assert fetched_user.email == "updated@example.com"

        # 删除
        db.delete(fetched_user)
        db.commit()
        deleted_user = db.query(User).filter(User.username == "dbtest").first()
        assert deleted_user is None

    def test_user_goal_relationship(self, db: Session):
        """测试用户和目标的关系"""
        # 创建用户
        user = User(
            username="relation_test",
            password_hash="hashed",
            email="relation@example.com"
        )
        db.add(user)
        db.commit()

        # 创建目标
        goal = Goal(
            user_id=user.id,
            title="关联测试目标",
            description="测试关系",
            status="planning"
        )
        db.add(goal)
        db.commit()

        # 验证关系
        db.refresh(user)
        assert len(user.goals) == 1
        assert user.goals[0].title == "关联测试目标"

    def test_cascade_delete(self, db: Session):
        """测试级联删除"""
        # 创建用户
        user = User(
            username="cascade_test",
            password_hash="hashed",
            email="cascade@example.com"
        )
        db.add(user)
        db.commit()

        # 创建目标
        goal = Goal(
            user_id=user.id,
            title="级联测试",
            description="测试级联删除",
            status="planning"
        )
        db.add(goal)
        db.commit()

        goal_id = goal.id

        # 删除用户
        db.delete(user)
        db.commit()

        # 验证目标也被删除
        deleted_goal = db.query(Goal).filter(Goal.id == goal_id).first()
        assert deleted_goal is None
