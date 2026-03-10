"""
Google Calendar API - 事件资源 (Events) 操作接口
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from core.base_client import GoogleCalendarBaseClient
from core.config import TIMEZONE, PRIMARY_CALENDAR_ID, MAX_RESULTS


class EventsService:
    """事件资源操作服务"""

    def __init__(self, client: GoogleCalendarBaseClient):
        """
        初始化事件服务

        Args:
            client: Google Calendar 基础客户端实例
        """
        self.client = client
        self.service = client.get_service().events()

    def get(self, event_id: str, calendar_id: str = PRIMARY_CALENDAR_ID) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单个事件

        Args:
            event_id: 事件ID
            calendar_id: 日历ID，默认为主日历

        Returns:
            Dict: 事件信息，包含以下主要字段：
                - id: 事件唯一标识符
                - summary: 事件标题
                - description: 事件描述
                - location: 地理位置信息
                - start/end: 开始/结束时间
                - attendees: 参与者列表
                - status: 事件状态
                - recurrence: 重复规则
                - reminders: 提醒设置

        Raises:
            HttpError: API调用失败
            Exception: 获取失败
        """
        try:
            response = self.service.get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取事件失败: {error_info}")

    def list(self, calendar_id: str = PRIMARY_CALENDAR_ID,
             time_min: Optional[datetime] = None,
             time_max: Optional[datetime] = None,
             max_results: int = MAX_RESULTS,
             q: Optional[str] = None,
             single_events: bool = True,
             order_by: str = 'startTime') -> List[Dict[str, Any]]:
        """
        列出日历中的事件

        Args:
            calendar_id: 日历ID，默认为主日历
            time_min: 查询开始时间（datetime对象）
            time_max: 查询结束时间（datetime对象）
            max_results: 最大结果数
            q: 搜索关键词（在标题、描述、位置等字段中搜索）
            single_events: 是否展开重复事件为单独实例
            order_by: 排序方式（'startTime' 或 'updated'）

        Returns:
            List[Dict]: 事件列表

        Raises:
            HttpError: API调用失败
            Exception: 查询失败
        """
        params = {
            'calendarId': calendar_id,
            'maxResults': max_results,
            'singleEvents': single_events,
            'orderBy': order_by
        }

        if time_min:
            params['timeMin'] = self.client._format_datetime(time_min)
        if time_max:
            params['timeMax'] = self.client._format_datetime(time_max)
        if q:
            params['q'] = q

        try:
            response = self.service.list(**params).execute()
            return response.get('items', [])
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"列出事件失败: {error_info}")

    def insert(self, summary: str, start: datetime, end: datetime,
               calendar_id: str = PRIMARY_CALENDAR_ID,
               description: Optional[str] = None,
               location: Optional[str] = None,
               attendees: Optional[List[Dict[str, str]]] = None,
               recurrence: Optional[List[str]] = None,
               reminders: Optional[Dict[str, Any]] = None,
               conference_data: Optional[Dict[str, Any]] = None,
               send_updates: str = 'none') -> Dict[str, Any]:
        """
        创建新事件

        Args:
            summary: 事件标题（必填）
            start: 开始时间（datetime对象）
            end: 结束时间（datetime对象）
            calendar_id: 日历ID，默认为主日历
            description: 事件描述
            location: 地理位置信息
            attendees: 参与者列表 [{'email': 'user@example.com'}, ...]
            recurrence: 重复规则（RRULE格式，如 ['RRULE:FREQ=WEEKLY;COUNT=10']）
            reminders: 提醒设置 {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 24}]}
            conference_data: 会议数据（用于Google Meet）
            send_updates: 更新通知方式（'none', 'externalOnly', 'all'）

        Returns:
            Dict: 新创建的事件信息

        Raises:
            HttpError: API调用失败
            Exception: 创建失败
        """
        event_body = {
            'summary': summary,
            'start': {'dateTime': self.client._format_datetime(start), 'timeZone': TIMEZONE},
            'end': {'dateTime': self.client._format_datetime(end), 'timeZone': TIMEZONE}
        }

        if description:
            event_body['description'] = description
        if location:
            event_body['location'] = location
        if attendees:
            event_body['attendees'] = attendees
        if recurrence:
            event_body['recurrence'] = recurrence
        if reminders:
            event_body['reminders'] = reminders
        if conference_data:
            event_body['conferenceData'] = conference_data

        params = {
            'calendarId': calendar_id,
            'body': event_body,
            'sendUpdates': send_updates
        }

        # 如果需要创建会议，设置conferenceDataVersion
        if conference_data:
            params['conferenceDataVersion'] = 1

        try:
            response = self.service.insert(**params).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"创建事件失败: {error_info}")

    def update(self, event_id: str, calendar_id: str = PRIMARY_CALENDAR_ID,
               summary: Optional[str] = None,
               start: Optional[datetime] = None,
               end: Optional[datetime] = None,
               **kwargs) -> Dict[str, Any]:
        """
        更新整个事件（完全替换）

        Args:
            event_id: 事件ID
            calendar_id: 日历ID
            summary: 新的事件标题
            start: 新的开始时间
            end: 新的结束时间
            **kwargs: 其他要更新的字段

        Returns:
            Dict: 更新后的事件信息

        Raises:
            HttpError: API调用失败
            Exception: 更新失败
        """
        # 先获取当前事件信息
        try:
            event = self.service.get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取事件信息失败: {error_info}")

        # 更新字段
        if summary is not None:
            event['summary'] = summary
        if start is not None:
            event['start'] = {'dateTime': self.client._format_datetime(start), 'timeZone': TIMEZONE}
        if end is not None:
            event['end'] = {'dateTime': self.client._format_datetime(end), 'timeZone': TIMEZONE}

        # 更新其他字段
        for key, value in kwargs.items():
            event[key] = value

        try:
            response = self.service.update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"更新事件失败: {error_info}")

    def patch(self, event_id: str, calendar_id: str = PRIMARY_CALENDAR_ID,
              **kwargs) -> Dict[str, Any]:
        """
        部分更新事件（补丁语义）

        Args:
            event_id: 事件ID
            calendar_id: 日历ID
            **kwargs: 要更新的字段（如 summary="新标题", location="新地点"）

        Returns:
            Dict: 更新后的事件信息

        Raises:
            HttpError: API调用失败
            Exception: 更新失败
        """
        try:
            response = self.service.patch(
                calendarId=calendar_id,
                eventId=event_id,
                body=kwargs
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"部分更新事件失败: {error_info}")

    def delete(self, event_id: str, calendar_id: str = PRIMARY_CALENDAR_ID,
               send_updates: str = 'none') -> bool:
        """
        删除事件

        Args:
            event_id: 事件ID
            calendar_id: 日历ID
            send_updates: 更新通知方式（'none', 'externalOnly', 'all'）

        Returns:
            bool: 删除成功返回True

        Raises:
            HttpError: API调用失败
            Exception: 删除失败
        """
        try:
            self.service.delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates=send_updates
            ).execute()
            return True
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"删除事件失败: {error_info}")

    def move(self, event_id: str, destination_calendar_id: str,
             source_calendar_id: str = PRIMARY_CALENDAR_ID) -> Dict[str, Any]:
        """
        将事件移动到其他日历

        Args:
            event_id: 事件ID
            destination_calendar_id: 目标日历ID
            source_calendar_id: 源日历ID，默认为主日历

        Returns:
            Dict: 移动后的事件信息

        Raises:
            HttpError: API调用失败
            Exception: 移动失败
        """
        try:
            response = self.service.move(
                calendarId=source_calendar_id,
                eventId=event_id,
                destination=destination_calendar_id
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"移动事件失败: {error_info}")

    def quick_add(self, text: str, calendar_id: str = PRIMARY_CALENDAR_ID,
                  send_updates: str = 'none') -> Dict[str, Any]:
        """
        通过文本字符串快速创建事件

        Args:
            text: 事件描述文本（如 "Dinner at 7pm tomorrow"）
            calendar_id: 日历ID
            send_updates: 更新通知方式

        Returns:
            Dict: 创建的事件信息

        Raises:
            HttpError: API调用失败
            Exception: 创建失败
        """
        try:
            response = self.service.quickAdd(
                calendarId=calendar_id,
                text=text,
                sendUpdates=send_updates
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"快速创建事件失败: {error_info}")

    def import_event(self, calendar_id: str = PRIMARY_CALENDAR_ID,
                     **event_body) -> Dict[str, Any]:
        """
        导入事件（仅限default类型）

        注意:
            - 此方法会触发与会者通知
            - 不支持从Gmail创建的事件

        Args:
            calendar_id: 日历ID
            **event_body: 事件主体内容

        Returns:
            Dict: 导入的事件信息

        Raises:
            HttpError: API调用失败
            Exception: 导入失败
        """
        try:
            response = self.service.import_(
                calendarId=calendar_id,
                body=event_body
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"导入事件失败: {error_info}")

    def instances(self, event_id: str, calendar_id: str = PRIMARY_CALENDAR_ID,
                  max_results: int = 250,
                  original_start: Optional[datetime] = None,
                  time_zone: str = TIMEZONE) -> List[Dict[str, Any]]:
        """
        获取重复事件的实例

        Args:
            event_id: 重复事件ID
            calendar_id: 日历ID
            max_results: 最大结果数
            original_start: 原始开始时间（用于定位特定实例）
            time_zone: 时区

        Returns:
            List[Dict]: 重复事件实例列表

        Raises:
            HttpError: API调用失败
            Exception: 查询失败
        """
        params = {
            'calendarId': calendar_id,
            'eventId': event_id,
            'maxResults': max_results
        }

        if original_start:
            params['originalStart'] = self.client._format_datetime(original_start)

        try:
            response = self.service.instances(**params).execute()
            return response.get('items', [])
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取重复事件实例失败: {error_info}")
