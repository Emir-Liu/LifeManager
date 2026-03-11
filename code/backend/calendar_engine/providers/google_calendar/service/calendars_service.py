"""
Google Calendar API - 日历资源 (Calendars) 操作接口
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from calendar_engine.providers.google_calendar.core.base_client import GoogleCalendarBaseClient
from calendar_engine.providers.google_calendar.core.config import TIMEZONE, PRIMARY_CALENDAR_ID


class CalendarsService:
    """日历资源操作服务"""

    def __init__(self, client: GoogleCalendarBaseClient):
        """
        初始化日历服务

        Args:
            client: Google Calendar 基础客户端实例
        """
        self.client = client
        self.service = client.get_service().calendars()

    def get(self, calendar_id: str = PRIMARY_CALENDAR_ID) -> Optional[Dict[str, Any]]:
        """
        获取指定日历的元数据

        Args:
            calendar_id: 日历ID，默认为主日历('primary')

        Returns:
            Dict: 日历元数据，包含以下字段：
                - kind: 资源类型 ("calendar#calendar")
                - etag: ETag用于并发控制
                - id: 日历唯一标识符
                - summary: 日历标题
                - description: 日历描述
                - location: 日历地理位置
                - timeZone: 日历时区
                - conferenceProperties: 会议属性

        Raises:
            HttpError: API调用失败
        """
        try:
            response = self.service.get(calendarId=calendar_id).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取日历失败: {error_info}")

    def insert(self, summary: str, description: str = None,
               location: str = None, time_zone: str = TIMEZONE) -> Dict[str, Any]:
        """
        创建次级日历

        Args:
            summary: 日历标题（必填）
            description: 日历描述（可选）
            location: 日历地理位置（可选）
            time_zone: 日历时区（可选，默认为 Asia/Shanghai）

        Returns:
            Dict: 新创建的日历信息

        Raises:
            HttpError: API调用失败
            Exception: 创建失败
        """
        calendar_body = {
            'summary': summary,
            'timeZone': time_zone
        }

        if description:
            calendar_body['description'] = description
        if location:
            calendar_body['location'] = location

        try:
            response = self.service.insert(body=calendar_body).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"创建日历失败: {error_info}")

    def update(self, calendar_id: str, summary: str = None,
               description: str = None, location: str = None,
               time_zone: str = None) -> Dict[str, Any]:
        """
        更新日历元数据（完全替换）

        Args:
            calendar_id: 日历ID
            summary: 新的日历标题
            description: 新的日历描述
            location: 新的日历地理位置
            time_zone: 新的日历时区

        Returns:
            Dict: 更新后的日历信息

        Raises:
            HttpError: API调用失败
            Exception: 更新失败
        """
        # 先获取当前日历信息
        try:
            calendar = self.service.get(calendarId=calendar_id).execute()
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取日历信息失败: {error_info}")

        # 更新字段
        if summary is not None:
            calendar['summary'] = summary
        if description is not None:
            calendar['description'] = description
        if location is not None:
            calendar['location'] = location
        if time_zone is not None:
            calendar['timeZone'] = time_zone

        try:
            response = self.service.update(
                calendarId=calendar_id,
                body=calendar
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"更新日历失败: {error_info}")

    def patch(self, calendar_id: str, **kwargs) -> Dict[str, Any]:
        """
        部分更新日历元数据（补丁语义）

        Args:
            calendar_id: 日历ID
            **kwargs: 要更新的字段（如 summary="新标题", timeZone="Asia/Shanghai"）

        Returns:
            Dict: 更新后的日历信息

        注意:
            每个patch请求消耗3个配额单位，建议先执行get再执行update

        Raises:
            HttpError: API调用失败
            Exception: 更新失败
        """
        try:
            response = self.service.patch(
                calendarId=calendar_id,
                body=kwargs
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"部分更新日历失败: {error_info}")

    def delete(self, calendar_id: str) -> bool:
        """
        删除次级日历

        Args:
            calendar_id: 要删除的日历ID

        Returns:
            bool: 删除成功返回True

        Raises:
            HttpError: API调用失败
            Exception: 删除失败
        """
        try:
            self.service.delete(calendarId=calendar_id).execute()
            return True
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"删除日历失败: {error_info}")

    def clear(self, calendar_id: str = PRIMARY_CALENDAR_ID) -> bool:
        """
        清空主日历（删除所有事件）

        注意:
            - 此操作只能用于主日历
            - 对于次级日历请使用delete方法

        Args:
            calendar_id: 日历ID（仅支持主日历）

        Returns:
            bool: 清空成功返回True

        Raises:
            HttpError: API调用失败
            Exception: 清空失败
        """
        try:
            self.service.clear(calendarId=calendar_id).execute()
            return True
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"清空日历失败: {error_info}")
