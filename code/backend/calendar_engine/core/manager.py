from typing import List, Dict, Optional
from calendar_engine.core.interface import CalendarProvider
from calendar_engine.core.models import Event, Calendar
from calendar_engine.core.factory import CalendarProviderFactory


class CalendarManager:
    """多日历管理器"""
    
    def __init__(self, providers: Optional[Dict[str, CalendarProvider]] = None, 
                 factory: Optional[CalendarProviderFactory] = None):
        """初始化日历管理器
        
        Args:
            providers: 提供者实例字典
            factory: 工厂实例,如果为None则自动创建
        """
        self.factory = factory or CalendarProviderFactory()
        self.providers = providers or {}
    
    def add_provider(self, provider_type: str, config: dict = None):
        """添加日历提供者
        
        Args:
            provider_type: 提供者类型
            config: 提供者配置
        """
        self.providers[provider_type] = self.factory.create(provider_type, config)
    
    def list_all_events(self, start_time: str, end_time: str) -> List[Event]:
        """聚合查询所有日历的事件
        
        Args:
            start_time: 开始时间 (ISO格式)
            end_time: 结束时间 (ISO格式)
            
        Returns:
            按时间排序的事件列表
        """
        all_events = []
        for provider in self.providers.values():
            calendars = provider.list_calendars()
            for calendar in calendars:
                events = provider.list_events(calendar.id, start_time, end_time)
                all_events.extend(events)
        return sorted(all_events, key=lambda e: e.start_time)
    
    def sync_event(self, event: Event, target_providers: List[str]) -> List[Event]:
        """跨日历同步事件
        
        Args:
            event: 要同步的事件
            target_providers: 目标日历提供者列表
            
        Returns:
            同步成功的事件列表
        """
        synced_events = []
        for provider_name in target_providers:
            provider = self.providers.get(provider_name)
            if provider:
                synced = provider.create_event(event.calendar_id, event)
                synced_events.append(synced)
        return synced_events
    
    def get_provider(self, provider_name: str) -> CalendarProvider:
        """获取指定提供者实例
        
        Args:
            provider_name: 提供者名称
            
        Returns:
            CalendarProvider实例
            
        Raises:
            ValueError: 如果提供者不存在
        """
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
        return provider

