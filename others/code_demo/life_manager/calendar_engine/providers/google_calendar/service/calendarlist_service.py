"""
Google Calendar API - 日历列表资源 (CalendarList) 操作接口
"""

from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from calendar_engine.providers.google_calendar.core.base_client import GoogleCalendarBaseClient
from calendar_engine.providers.google_calendar.core.config import MAX_RESULTS


class CalendarListService:
    """日历列表资源操作服务"""

    def __init__(self, client: GoogleCalendarBaseClient):
        """
        初始化日历列表服务

        Args:
            client: Google Calendar 基础客户端实例
        """
        self.client = client
        self.service = client.get_service().calendarList()

    def list(self, min_access_role: Optional[str] = None,
             max_results: int = MAX_RESULTS,
             page_token: Optional[str] = None,
             show_hidden: Optional[bool] = None,
             show_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        返回用户日历列表中的所有日历

        Args:
            min_access_role: 最小访问角色过滤
                - 'freeBusyReader': 仅查看忙闲信息
                - 'reader': 查看日历
                - 'writer': 读写日历
                - 'owner': 管理权限
            max_results: 最大结果数
            page_token: 分页令牌（用于获取下一页）
            show_hidden: 是否显示隐藏的日历
            show_deleted: 是否显示已删除的日历

        Returns:
            List[Dict]: 日历列表，每个日历包含：
                - kind: 资源类型
                - etag: ETag
                - id: 日历标识符
                - summary: 日历标题
                - description: 日历描述
                - location: 日历地理位置
                - timeZone: 日历时区
                - summaryOverride: 用户设置的日历摘要覆盖
                - colorId: 日历颜色ID
                - backgroundColor: 日历背景色
                - foregroundColor: 日历前景色
                - hidden: 是否在列表中隐藏
                - selected: 是否在日历UI中显示内容
                - accessRole: 用户的访问角色
                - defaultReminders: 默认提醒设置
                - notificationSettings: 通知设置
                - primary: 是否是用户的主日历

        Raises:
            HttpError: API调用失败
            Exception: 查询失败
        """
        params = {
            'maxResults': max_results,
            'showDeleted': show_deleted
        }

        if min_access_role:
            params['minAccessRole'] = min_access_role
        if page_token:
            params['pageToken'] = page_token
        if show_hidden is not None:
            params['showHidden'] = show_hidden

        try:
            response = self.service.list(**params).execute()
            return response.get('items', [])
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取日历列表失败: {error_info}")

    def get(self, calendar_id: str) -> Dict[str, Any]:
        """
        获取用户日历列表中的特定日历

        Args:
            calendar_id: 日历ID

        Returns:
            Dict: 日历信息

        Raises:
            HttpError: API调用失败
            Exception: 获取失败
        """
        try:
            response = self.service.get(calendarId=calendar_id).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取日历失败: {error_info}")

    def insert(self, calendar_id: str, summary_override: Optional[str] = None,
               color_id: Optional[str] = None,
               background_color: Optional[str] = None,
               foreground_color: Optional[str] = None,
               hidden: bool = False,
               selected: bool = True,
               default_reminders: Optional[List[Dict[str, Any]]] = None,
               notification_settings: Optional[Dict[str, Any]] = None,
               color_rgb_format: bool = False) -> Dict[str, Any]:
        """
        将现有日历插入用户日历列表

        注意:
            - 设置颜色相关属性时需要指定colorRgbFormat=true
            - 如果日历已在列表中，将返回400错误

        Args:
            calendar_id: 要插入的日历ID（必填）
            summary_override: 用户设置的日历摘要覆盖
            color_id: 日历颜色ID（1-11）
            background_color: 日历背景色（十六进制格式）
            foreground_color: 日历前景色（十六进制格式）
            hidden: 是否在列表中隐藏
            selected: 是否在日历UI中显示内容
            default_reminders: 默认提醒设置 [{'method': 'email', 'minutes': 60}, ...]
            notification_settings: 通知设置
            color_rgb_format: 是否使用RGB格式颜色

        Returns:
            Dict: 插入的日历信息

        Raises:
            HttpError: API调用失败
            Exception: 插入失败
        """
        body = {
            'id': calendar_id,
            'hidden': hidden,
            'selected': selected
        }

        if summary_override:
            body['summaryOverride'] = summary_override
        if color_id:
            body['colorId'] = color_id
        if background_color:
            body['backgroundColor'] = background_color
        if foreground_color:
            body['foregroundColor'] = foreground_color
        if default_reminders:
            body['defaultReminders'] = default_reminders
        if notification_settings:
            body['notificationSettings'] = notification_settings

        params = {
            'body': body
        }

        if color_rgb_format and (background_color or foreground_color):
            params['colorRgbFormat'] = True

        try:
            response = self.service.insert(**params).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"插入日历失败: {error_info}")

    def update(self, calendar_id: str, **kwargs) -> Dict[str, Any]:
        """
        更新日历列表中的日历（完全替换）

        Args:
            calendar_id: 日历ID
            **kwargs: 要更新的字段

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
        for key, value in kwargs.items():
            calendar[key] = value

        try:
            response = self.service.update(
                calendarId=calendar_id,
                body=calendar
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"更新日历列表失败: {error_info}")

    def patch(self, calendar_id: str, color_rgb_format: bool = False,
              **kwargs) -> Dict[str, Any]:
        """
        部分更新日历列表中的日历（补丁语义）

        注意:
            每个patch请求会消耗3个配额单位，建议先get再update

        Args:
            calendar_id: 日历ID
            color_rgb_format: 是否使用RGB格式颜色
            **kwargs: 要更新的字段

        Returns:
            Dict: 更新后的日历信息

        Raises:
            HttpError: API调用失败
            Exception: 更新失败
        """
        params = {
            'calendarId': calendar_id,
            'body': kwargs
        }

        if color_rgb_format:
            params['colorRgbFormat'] = True

        try:
            response = self.service.patch(**params).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"部分更新日历列表失败: {error_info}")

    def delete(self, calendar_id: str) -> bool:
        """
        从用户日历列表中移除日历

        注意:
            - 此操作不会删除日历本身，只是从列表中移除
            - 要删除日历，请使用Calendars.delete方法

        Args:
            calendar_id: 日历ID

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
            raise Exception(f"从日历列表中移除日历失败: {error_info}")

    def watch(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        监听CalendarList资源的变化

        Args:
            body: 包含监听配置的字典：
                {
                    'id': '监听通道的唯一ID',
                    'type': 'web_hook',
                    'address': '接收通知的Webhook URL',
                    'params': {
                        'ttl': '通道令牌的TTL（毫秒）'
                    },
                    'token': '可选的令牌字符串'
                }

        Returns:
            Dict: 监听响应，包含：
                - id: 监听通道ID
                - resourceId: 资源ID
                - resourceUri: 资源URI
                - expiration: 过期时间

        Raises:
            HttpError: API调用失败
            Exception: 监听失败
        """
        try:
            response = self.service.watch(body=body).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"监听CalendarList失败: {error_info}")

    def stop(self, channel_id: str, resource_id: str) -> bool:
        """
        停止监听资源

        Args:
            channel_id: 监听通道ID
            resource_id: 资源ID

        Returns:
            bool: 停止成功返回True

        Raises:
            HttpError: API调用失败
            Exception: 停止失败
        """
        # 注意：stop方法在channels资源中，这里提供一个封装
        # 实际调用应该通过client.service.channels().stop()
        # 此方法仅为示例，实际实现需要使用channels资源
        raise NotImplementedError("请使用 ChannelsService.stop() 方法")
