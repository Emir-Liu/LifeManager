"""
Google Calendar API 统一客户端
整合所有服务模块，提供统一的访问接口
"""

from calendar_engine.providers.google_calendar.core.base_client import GoogleCalendarBaseClient
from calendar_engine.providers.google_calendar.core.config import CLIENT_SECRET_FILE
from calendar_engine.providers.google_calendar.service.calendars_service import CalendarsService
from calendar_engine.providers.google_calendar.service.events_service import EventsService
from calendar_engine.providers.google_calendar.service.calendarlist_service import CalendarListService
from calendar_engine.providers.google_calendar.service.acl_service import AclService
from calendar_engine.providers.google_calendar.service.freebusy_service import FreebusyService
from calendar_engine.providers.google_calendar.service.settings_service import SettingsService
from calendar_engine.providers.google_calendar.service.channels_service import ChannelsService


class GoogleCalendarClient:
    """Google Calendar API 统一客户端"""

    def __init__(self, credentials_file: str = CLIENT_SECRET_FILE,
                 token_file: str = 'token.json'):
        """
        初始化 Google Calendar 统一客户端

        Args:
            credentials_file: OAuth 客户端密钥文件路径
            token_file: 存储的凭据文件路径
        """
        # 初始化基础客户端
        self.base_client = GoogleCalendarBaseClient(credentials_file, token_file)

        # 初始化各个服务
        self.calendars = CalendarsService(self.base_client)
        self.events = EventsService(self.base_client)
        self.calendar_list = CalendarListService(self.base_client)
        self.acl = AclService(self.base_client)
        self.freebusy = FreebusyService(self.base_client)
        self.settings = SettingsService(self.base_client)
        self.channels = ChannelsService(self.base_client)

    def get_base_client(self) -> GoogleCalendarBaseClient:
        """
        获取基础客户端实例

        Returns:
            GoogleCalendarBaseClient: 基础客户端实例
        """
        return self.base_client

    def get_service(self):
        """
        获取 Google Calendar API 服务对象

        Returns:
            Resource: Google Calendar API 服务对象
        """
        return self.base_client.get_service()

    def refresh_credentials(self) -> None:
        """
        刷新认证凭证
        """
        # 重新初始化基础客户端会自动刷新凭证
        self.base_client = GoogleCalendarBaseClient(
            self.base_client.credentials._refresh_token,
            'token.json'
        )

        # 重新初始化所有服务
        self.calendars = CalendarsService(self.base_client)
        self.events = EventsService(self.base_client)
        self.calendar_list = CalendarListService(self.base_client)
        self.acl = AclService(self.base_client)
        self.freebusy = FreebusyService(self.base_client)
        self.settings = SettingsService(self.base_client)
        self.channels = ChannelsService(self.base_client)
