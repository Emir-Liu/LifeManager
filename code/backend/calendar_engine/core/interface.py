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
    def delete_event(self, event_id: str) -> bool:
        """删除事件
        
        Args:
            event_id: 事件ID
            
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
