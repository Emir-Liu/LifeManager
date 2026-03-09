"""
TimePreference Service (Sync Version)
时间偏好服务 - 同步版本
"""
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.time_preference import TimePreference
from app.schemas.time_preference import (
    TimePreferenceCreate,
    TimePreferenceUpdate,
    TimeStatsResponse,
)


class TimePreferenceServiceSync:
    """时间偏好服务 - 同步版本"""

    def __init__(self, db: Session):
        self.db = db

    def create_time_preference(self, user_id: int, data: TimePreferenceCreate) -> TimePreference:
        """创建时间偏好"""
        preference = TimePreference(
            user_id=user_id,
            preferred_start_time=data.preferred_start_time,
            preferred_end_time=data.preferred_end_time,
            break_duration=data.break_duration,
            max_continuous_work=data.max_continuous_work,
            work_days=data.work_days,
        )
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        return preference

    def get_user_time_preference(self, user_id: int) -> Optional[TimePreference]:
        """获取用户时间偏好"""
        result = self.db.execute(
            select(TimePreference).where(TimePreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    def update_time_preference(
        self, user_id: int, data: TimePreferenceUpdate
    ) -> Optional[TimePreference]:
        """更新时间偏好"""
        preference = self.get_user_time_preference(user_id)
        if not preference:
            return None

        # 更新字段
        if data.preferred_start_time is not None:
            preference.preferred_start_time = data.preferred_start_time
        if data.preferred_end_time is not None:
            preference.preferred_end_time = data.preferred_end_time
        if data.break_duration is not None:
            preference.break_duration = data.break_duration
        if data.max_continuous_work is not None:
            preference.max_continuous_work = data.max_continuous_work
        if data.work_days is not None:
            preference.work_days = data.work_days

        self.db.commit()
        self.db.refresh(preference)
        return preference

    def get_time_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> TimeStatsResponse:
        """获取时间统计 - 简化版本"""
        # 暂时返回空统计
        return TimeStatsResponse(
            total_hours=0,
            productive_hours=0,
            break_hours=0,
            avg_daily_hours=0,
            most_productive_day="Monday",
            efficiency_score=0,
        )
