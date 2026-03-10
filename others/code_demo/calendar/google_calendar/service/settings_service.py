"""
Google Calendar API - 设置资源 (Settings) 操作接口
"""

from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from core.base_client import GoogleCalendarBaseClient


class SettingsService:
    """设置资源操作服务"""

    def __init__(self, client: GoogleCalendarBaseClient):
        """
        初始化设置服务

        Args:
            client: Google Calendar 基础客户端实例
        """
        self.client = client
        self.service = client.get_service().settings()

    def list(self, max_results: int = 100,
             page_token: Optional[str] = None,
             sync_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        返回认证用户的所有用户设置

        注意:
            如果某个设置保持其默认值，它可能不会被返回

        Args:
            max_results: 最大结果数
            page_token: 分页令牌
            sync_token: 同步令牌（用于增量同步）

        Returns:
            List[Dict]: 设置列表，每个设置包含：
                - kind: 资源类型 ("calendar#setting")
                - etag: ETag
                - id: 设置ID
                - value: 设置值

        Raises:
            HttpError: API调用失败
            Exception: 查询失败
        """
        params = {
            'maxResults': max_results
        }

        if page_token:
            params['pageToken'] = page_token
        if sync_token:
            params['syncToken'] = sync_token

        try:
            response = self.service.list(**params).execute()
            return response.get('items', [])
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取设置列表失败: {error_info}")

    def get(self, setting_id: str) -> Dict[str, Any]:
        """
        返回单个用户设置

        Args:
            setting_id: 设置ID

        Returns:
            Dict: 设置信息

        Raises:
            HttpError: API调用失败
            Exception: 获取失败
        """
        try:
            response = self.service.get(setting=setting_id).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取设置失败: {error_info}")

    def watch(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        监听Settings资源的更改

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
            raise Exception(f"监听Settings失败: {error_info}")

    def get_timezone(self) -> Optional[str]:
        """
        获取用户时区设置

        Returns:
            str: 时区ID（如 'Asia/Shanghai'），如果未设置则返回None

        Raises:
            Exception: 获取失败
        """
        try:
            setting = self.get('timezone')
            return setting.get('value')
        except Exception as e:
            raise Exception(f"获取时区设置失败: {str(e)}")

    def get_locale(self) -> Optional[str]:
        """
        获取用户区域设置

        Returns:
            str: 区域设置代码（如 'zh_CN', 'en'），如果未设置则返回None

        Raises:
            Exception: 获取失败
        """
        try:
            setting = self.get('locale')
            return setting.get('value')
        except Exception as e:
            raise Exception(f"获取区域设置失败: {str(e)}")

    def get_week_start(self) -> Optional[int]:
        """
        获取一周开始日设置

        Returns:
            int: 一周从周几开始（0=周日, 1=周一, 6=周六），如果未设置则返回None

        Raises:
            Exception: 获取失败
        """
        try:
            setting = self.get('weekStart')
            value = setting.get('value')
            return int(value) if value else None
        except Exception as e:
            raise Exception(f"获取一周开始日设置失败: {str(e)}")

    def get_default_event_length(self) -> Optional[int]:
        """
        获取默认事件长度设置

        Returns:
            int: 默认事件长度（分钟），如果未设置则返回None

        Raises:
            Exception: 获取失败
        """
        try:
            setting = self.get('defaultEventLength')
            value = setting.get('value')
            return int(value) if value else None
        except Exception as e:
            raise Exception(f"获取默认事件长度设置失败: {str(e)}")

    def get_format24_hour_time(self) -> Optional[bool]:
        """
        获取24小时制时间显示设置

        Returns:
            bool: 是否使用24小时制，如果未设置则返回None

        Raises:
            Exception: 获取失败
        """
        try:
            setting = self.get('format24HourTime')
            value = setting.get('value')
            return value.lower() == 'true' if value else None
        except Exception as e:
            raise Exception(f"获取24小时制设置失败: {str(e)}")

    def get_auto_add_hangouts(self) -> Optional[bool]:
        """
        获取自动添加视频会议设置

        Returns:
            bool: 是否自动添加视频会议，如果未设置则返回None

        Raises:
            Exception: 获取失败
        """
        try:
            setting = self.get('autoAddHangouts')
            value = setting.get('value')
            return value.lower() == 'true' if value else None
        except Exception as e:
            raise Exception(f"获取自动添加视频会议设置失败: {str(e)}")

    def get_all_settings_dict(self) -> Dict[str, Any]:
        """
        获取所有设置并转换为字典

        Returns:
            Dict: 设置字典，键为设置ID，值为设置值

        Raises:
            Exception: 获取失败
        """
        try:
            settings_list = self.list()
            settings_dict = {}
            for setting in settings_list:
                settings_dict[setting['id']] = setting['value']
            return settings_dict
        except Exception as e:
            raise Exception(f"获取所有设置失败: {str(e)}")
