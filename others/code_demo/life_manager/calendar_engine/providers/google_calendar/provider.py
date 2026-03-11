from typing import List, Optional
from datetime import datetime
from calendar_engine.core.interface import CalendarProvider
from calendar_engine.core.models import Event, Calendar


class GoogleCalendarProvider(CalendarProvider):
    """Google Calendar 提供者实现"""
    
    def __init__(self, credentials_path: str, token_path: str):
        """初始化Google Calendar提供者
        
        Args:
            credentials_path: OAuth客户端密钥文件路径
            token_path: 存储的凭证文件路径
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._client = None
        self._events_service = None
        self._calendarlist_service = None
    
    def _get_client(self):
        """获取Google Calendar客户端(延迟初始化)"""
        if self._client is None:
            from calendar_engine.providers.google_calendar.core.base_client import GoogleCalendarBaseClient
            self._client = GoogleCalendarBaseClient(
                credentials_file=self.credentials_path,
                token_file=self.token_path
            )
        return self._client
    
    def _get_events_service(self):
        """获取事件服务"""
        if self._events_service is None:
            from calendar_engine.providers.google_calendar.service.events_service import EventsService
            client = self._get_client()
            self._events_service = EventsService(client)
        return self._events_service
    
    def _get_calendarlist_service(self):
        """获取日历列表服务"""
        if self._calendarlist_service is None:
            from calendar_engine.providers.google_calendar.service.calendarlist_service import CalendarListService
            client = self._get_client()
            self._calendarlist_service = CalendarListService(client)
        return self._calendarlist_service
    
    def _parse_event(self, event_dict: dict, calendar_id: str) -> Event:
        """解析Google Calendar API返回的事件为统一Event模型
        
        Args:
            event_dict: Google Calendar API返回的事件字典
            calendar_id: 日历ID
            
        Returns:
            Event实例
        """
        # 处理开始时间
        start_data = event_dict.get('start', {})
        if 'dateTime' in start_data:
            start_time = start_data['dateTime']
        elif 'date' in start_data:
            start_time = start_data['date']
        else:
            start_time = None
        
        # 处理结束时间
        end_data = event_dict.get('end', {})
        if 'dateTime' in end_data:
            end_time = end_data['dateTime']
        elif 'date' in end_data:
            end_time = end_data['date']
        else:
            end_time = None
        
        # 处理参与者
        attendees_list = event_dict.get('attendees', [])
        attendees = [a.get('email') for a in attendees_list if a.get('email')]
        
        return Event(
            id=event_dict.get('id', ''),
            calendar_id=calendar_id,
            summary=event_dict.get('summary', ''),
            start_time=start_time,
            end_time=end_time,
            description=event_dict.get('description'),
            location=event_dict.get('location'),
            attendees=attendees if attendees else None,
            status=event_dict.get('status')
        )
    
    def _parse_calendar(self, calendar_dict: dict) -> Calendar:
        """解析Google Calendar API返回的日历为统一Calendar模型
        
        Args:
            calendar_dict: Google Calendar API返回的日历字典
            
        Returns:
            Calendar实例
        """
        return Calendar(
            id=calendar_dict.get('id', ''),
            summary=calendar_dict.get('summary', ''),
            description=calendar_dict.get('description'),
            primary=calendar_dict.get('primary', False),
            color_id=calendar_dict.get('colorId')
        )
    
    def list_events(self, calendar_id: str, start_time: str, end_time: str) -> List[Event]:
        """获取事件列表
        
        Args:
            calendar_id: 日历ID
            start_time: 开始时间 (ISO格式)
            end_time: 结束时间 (ISO格式)
            
        Returns:
            事件列表
        """
        service = self._get_events_service()
        
        # 转换ISO格式字符串为datetime对象
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if start_time else None
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else None
        
        # 调用Google Calendar API
        event_dicts = service.list(
            calendar_id=calendar_id,
            time_min=start_dt,
            time_max=end_dt
        )
        
        # 解析为统一Event模型
        events = []
        for event_dict in event_dicts:
            event = self._parse_event(event_dict, calendar_id)
            events.append(event)
        
        return events
    
    def create_event(self, calendar_id: str, event: Event) -> Event:
        """创建事件
        
        Args:
            calendar_id: 日历ID
            event: 事件对象
            
        Returns:
            创建的事件
        """
        service = self._get_events_service()
        
        # 转换ISO格式字符串为datetime对象
        start_dt = datetime.fromisoformat(event.start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(event.end_time.replace('Z', '+00:00'))
        
        # 构建参与者列表
        attendees = None
        if event.attendees:
            attendees = [{'email': email} for email in event.attendees]
        
        # 调用Google Calendar API
        result_dict = service.insert(
            summary=event.summary,
            start=start_dt,
            end=end_dt,
            calendar_id=calendar_id,
            description=event.description,
            location=event.location,
            attendees=attendees
        )
        
        # 解析返回的事件
        return self._parse_event(result_dict, calendar_id)
    
    def update_event(self, event_id: str, event: Event) -> Event:
        """更新事件
        
        Args:
            event_id: 事件ID
            event: 更新的事件对象
            
        Returns:
            更新后的事件
        """
        service = self._get_events_service()
        
        # 转换ISO格式字符串为datetime对象
        start_dt = datetime.fromisoformat(event.start_time.replace('Z', '+00:00')) if event.start_time else None
        end_dt = datetime.fromisoformat(event.end_time.replace('Z', '+00:00')) if event.end_time else None
        
        # 构建参与者列表
        attendees = None
        if event.attendees:
            attendees = [{'email': email} for email in event.attendees]
        
        # 调用Google Calendar API
        result_dict = service.update(
            event_id=event_id,
            calendar_id=event.calendar_id,
            summary=event.summary,
            start=start_dt,
            end=end_dt,
            description=event.description,
            location=event.location,
            attendees=attendees
        )
        
        # 解析返回的事件
        return self._parse_event(result_dict, event.calendar_id)
    
    def delete_event(self, event_id: str) -> bool:
        """删除事件
        
        Args:
            event_id: 事件ID
            
        Returns:
            是否删除成功
        """
        service = self._get_events_service()
        return service.delete(event_id=event_id)
    
    def get_event(self, event_id: str) -> Event:
        """获取事件详情
        
        Args:
            event_id: 事件ID
            
        Returns:
            事件详情
        """
        service = self._get_events_service()
        event_dict = service.get(event_id=event_id)
        
        # 从事件字典中获取日历ID
        calendar_id = event_dict.get('organizer', {}).get('email', '').split('@')[0] or 'primary'
        
        return self._parse_event(event_dict, calendar_id)
    
    def list_calendars(self) -> List[Calendar]:
        """获取日历列表
        
        Returns:
            日历列表
        """
        service = self._get_calendarlist_service()
        calendar_dicts = service.list()
        
        # 解析为统一Calendar模型
        calendars = []
        for calendar_dict in calendar_dicts:
            calendar = self._parse_calendar(calendar_dict)
            calendars.append(calendar)
        
        return calendars
