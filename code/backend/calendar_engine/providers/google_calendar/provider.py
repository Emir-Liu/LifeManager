from typing import List, Optional
from datetime import datetime, timedelta, timezone
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

    def _parse_iso_to_datetime(self, iso_string: str):
        """解析ISO格式字符串为datetime对象，并附加东八区时区

        Args:
            iso_string: ISO格式的时间字符串（如 "2024-03-11T07:00:00"）

        Returns:
            datetime: 带东八区时区的datetime对象
        """
        # 解析ISO字符串
        dt = datetime.fromisoformat(iso_string)

        # 如果没有时区信息，添加东八区（UTC+8）
        if dt.tzinfo is None:
            tz = timezone(timedelta(hours=8))
            dt = dt.replace(tzinfo=tz)

        return dt
    
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

        # 转换ISO格式字符串为datetime对象（带东八区时区）
        start_dt = self._parse_iso_to_datetime(start_time) if start_time else None
        end_dt = self._parse_iso_to_datetime(end_time) if end_time else None

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

        # 转换ISO格式字符串为datetime对象（带东八区时区）
        start_dt = self._parse_iso_to_datetime(event.start_time)
        end_dt = self._parse_iso_to_datetime(event.end_time)

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

        # 转换ISO格式字符串为datetime对象（带东八区时区）
        start_dt = self._parse_iso_to_datetime(event.start_time) if event.start_time else None
        end_dt = self._parse_iso_to_datetime(event.end_time) if event.end_time else None

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
    
    def delete_event(self, event_id: str, calendar_id: str) -> bool:
        """删除事件

        Args:
            event_id: 事件ID
            calendar_id: 日历ID

        Returns:
            是否删除成功
        """
        service = self._get_events_service()
        return service.delete(event_id=event_id, calendar_id=calendar_id)
    
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

    def clear_calendar(self, calendar_id: str) -> bool:
        """清空日历（删除所有事件）

        Args:
            calendar_id: 日历ID

        Returns:
            是否清空成功
        """
        service = self._get_events_service()
        return service.clear(calendar_id=calendar_id)

    def delete_calendar(self, calendar_id: str) -> bool:
        """删除日历

        Args:
            calendar_id: 日历ID

        Returns:
            是否删除成功
        """
        from calendar_engine.providers.google_calendar.service.calendars_service import CalendarsService
        client = self._get_client()
        service = CalendarsService(client)
        return service.delete(calendar_id=calendar_id)

    def create_calendar(self, summary: str, description: str) -> Calendar:
        """创建新日历

        Args:
            summary: 日历标题
            description: 日历描述

        Returns:
            创建的日历
        """
        from calendar_engine.providers.google_calendar.service.calendars_service import CalendarsService
        client = self._get_client()
        service = CalendarsService(client)
        result_dict = service.insert(summary=summary, description=description)
        return self._parse_calendar(result_dict)

    def get_calendar(self, calendar_id: str) -> Calendar:
        """获取日历详情

        Args:
            calendar_id: 日历ID

        Returns:
            日历详情
        """
        from calendar_engine.providers.google_calendar.service.calendars_service import CalendarsService
        client = self._get_client()
        service = CalendarsService(client)
        result_dict = service.get(calendar_id=calendar_id)
        return self._parse_calendar(result_dict)

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
        from calendar_engine.providers.google_calendar.service.calendars_service import CalendarsService
        client = self._get_client()
        service = CalendarsService(client)
        result_dict = service.update(
            calendar_id=calendar_id,
            summary=summary,
            description=description,
            location=location
        )
        return self._parse_calendar(result_dict)

    def list_recurring_events(self, calendar_id: str, start_time: str = None, end_time: str = None) -> List[Event]:
        """查询重复事件列表

        Args:
            calendar_id: 日历ID
            start_time: 开始时间 (ISO格式)
            end_time: 结束时间 (ISO格式)

        Returns:
            重复事件列表
        """
        service = self._get_events_service()

        # 转换ISO格式字符串为datetime对象（带东八区时区）
        start_dt = self._parse_iso_to_datetime(start_time) if start_time else None
        end_dt = self._parse_iso_to_datetime(end_time) if end_time else None

        # 调用Google Calendar API
        event_dicts = service.list_recurring(
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

    def create_recurring_event(self, calendar_id: str, event: Event, recurrence_rule: str) -> Event:
        """创建重复事件

        Args:
            calendar_id: 日历ID
            event: 事件对象
            recurrence_rule: 重复规则 (RRULE格式，如 "FREQ=WEEKLY;COUNT=10")

        Returns:
            创建的重复事件
        """
        service = self._get_events_service()

        # 转换ISO格式字符串为datetime对象（带东八区时区）
        start_dt = self._parse_iso_to_datetime(event.start_time)
        end_dt = self._parse_iso_to_datetime(event.end_time)

        # 构建参与者列表
        attendees = None
        if event.attendees:
            attendees = [{'email': email} for email in event.attendees]

        # 调用Google Calendar API
        result_dict = service.insert_recurring(
            summary=event.summary,
            start=start_dt,
            end=end_dt,
            recurrence=recurrence_rule,
            calendar_id=calendar_id,
            description=event.description,
            location=event.location,
            attendees=attendees
        )

        # 解析返回的事件
        return self._parse_event(result_dict, calendar_id)

    def update_recurring_event(self, event_id: str, calendar_id: str, event: Event,
                                update_scope: str = "future") -> Event:
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
        service = self._get_events_service()

        # 转换ISO格式字符串为datetime对象（带东八区时区）
        start_dt = self._parse_iso_to_datetime(event.start_time) if event.start_time else None
        end_dt = self._parse_iso_to_datetime(event.end_time) if event.end_time else None

        # 构建参与者列表
        attendees = None
        if event.attendees:
            attendees = [{'email': email} for email in event.attendees]

        # 调用Google Calendar API
        result_dict = service.update_recurring(
            event_id=event_id,
            calendar_id=calendar_id,
            summary=event.summary,
            start=start_dt,
            end=end_dt,
            update_scope=update_scope,
            description=event.description,
            location=event.location,
            attendees=attendees
        )

        # 解析返回的事件
        return self._parse_event(result_dict, calendar_id)

    def delete_recurring_event(self, event_id: str, calendar_id: str, delete_scope: str = "future") -> bool:
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
        service = self._get_events_service()
        return service.delete_recurring(
            event_id=event_id,
            calendar_id=calendar_id,
            delete_scope=delete_scope
        )

    def get_recurring_event_instances(self, event_id: str, calendar_id: str) -> List[Event]:
        """获取重复事件的所有实例

        Args:
            event_id: 重复事件ID
            calendar_id: 日历ID

        Returns:
            重复事件实例列表
        """
        service = self._get_events_service()

        # 调用Google Calendar API
        event_dicts = service.get_instances(
            event_id=event_id,
            calendar_id=calendar_id
        )

        # 解析为统一Event模型
        events = []
        for event_dict in event_dicts:
            event = self._parse_event(event_dict, calendar_id)
            events.append(event)

        return events
