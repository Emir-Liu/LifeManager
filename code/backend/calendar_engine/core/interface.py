from abc import ABC, abstractmethod
from typing import List, Optional
from calendar_engine.core.models import Event, Calendar


class CalendarProvider(ABC):
    """日历提供者抽象接口"""

    @abstractmethod
    def list_events(self, calendar_id: str, start_time: str, end_time: str) -> List[Event]:
        """获取事件列表

        Args:
            calendar_id: 日历ID
            start_time: 开始时间 (ISO格式)
            end_time: 结束时间 (ISO格式)

        Returns:
            事件列表
        """
        pass

    @abstractmethod
    def create_event(self, calendar_id: str, event: Event) -> Event:
        """创建事件

        Args:
            calendar_id: 日历ID
            event: 事件对象

        Returns:
            创建的事件
        """
        pass

    @abstractmethod
    def update_event(self, event_id: str, event: Event) -> Event:
        """更新事件

        Args:
            event_id: 事件ID
            event: 更新的事件对象

        Returns:
            更新后的事件
        """
        pass

    @abstractmethod
    def delete_event(self, event_id: str, calendar_id: str) -> bool:
        """删除事件

        Args:
            event_id: 事件ID
            calendar_id: 日历ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Event:
        """获取事件详情

        Args:
            event_id: 事件ID

        Returns:
            事件详情
        """
        pass

    @abstractmethod
    def list_calendars(self) -> List[Calendar]:
        """获取日历列表

        Returns:
            日历列表
        """
        pass

    @abstractmethod
    def clear_calendar(self, calendar_id: str) -> bool:
        """清空日历（删除所有事件）

        Args:
            calendar_id: 日历ID

        Returns:
            是否清空成功
        """
        pass

    @abstractmethod
    def delete_calendar(self, calendar_id: str) -> bool:
        """删除日历

        Args:
            calendar_id: 日历ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def create_calendar(self, summary: str, description: str) -> Calendar:
        """创建新日历

        Args:
            summary: 日历标题
            description: 日历描述

        Returns:
            创建的日历
        """
        pass

    @abstractmethod
    def get_calendar(self, calendar_id: str) -> Calendar:
        """获取日历详情

        Args:
            calendar_id: 日历ID

        Returns:
            日历详情
        """
        pass

    @abstractmethod
    def update_calendar(self, calendar_id: str, summary: str = None,
                    description: str = None, location: str = None) -> Calendar:
        """更新日历信息

        Args:
            calendar_id: 日历ID
            summary: 日历标题
            description: 日历描述
            location: 日历位置

        Returns:
            更新后的日历
        """
        pass

    @abstractmethod
    def list_recurring_events(self, calendar_id: str, start_time: str = None, end_time: str = None):
        """查询重复事件列表

        Args:
            calendar_id: 日历ID
            start_time: 开始时间 (ISO格式)
            end_time: 结束时间 (ISO格式)

        Returns:
            重复事件列表
        """
        pass

    @abstractmethod
    def create_recurring_event(self, calendar_id: str, event: Event, recurrence_rule: str):
        """创建重复事件

        Args:
            calendar_id: 日历ID
            event: 事件对象
            recurrence_rule: 重复规则 (RRULE格式，如 "FREQ=WEEKLY;COUNT=10")

        Returns:
            创建的重复事件
        """
        pass

    @abstractmethod
    def update_recurring_event(self, event_id: str, calendar_id: str, event: Event,
                                update_scope: str = "future"):
        """更新重复事件

        Args:
            event_id: 事件ID
            calendar_id: 日历ID
            event: 更新的事件对象
            update_scope: 更新范围
                - "future": 更新此实例及所有未来实例
                - "all": 更新所有实例
                - "single": 只更新此实例

        Returns:
            更新后的事件
        """
        pass

    @abstractmethod
    def delete_recurring_event(self, event_id: str, calendar_id: str, delete_scope: str = "future"):
        """删除重复事件

        Args:
            event_id: 事件ID
            calendar_id: 日历ID
            delete_scope: 删除范围
                - "future": 删除此实例及所有未来实例
                - "all": 删除所有实例
                - "single": 只删除此实例

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    def get_recurring_event_instances(self, event_id: str, calendar_id: str):
        """获取重复事件的所有实例

        Args:
            event_id: 重复事件ID
            calendar_id: 日历ID

        Returns:
            重复事件实例列表
        """
        pass
