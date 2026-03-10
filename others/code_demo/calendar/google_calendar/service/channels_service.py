"""
Google Calendar API - 通道资源 (Channels) 操作接口
"""

from typing import Dict, Any, Optional
from googleapiclient.errors import HttpError


class ChannelsService:
    """通道资源操作服务"""

    def __init__(self, client):
        """
        初始化通道服务

        Args:
            client: Google Calendar 基础客户端实例
        """
        self.client = client
        self.service = client.get_service().channels()

    def stop(self, body: Dict[str, Any]) -> bool:
        """
        停止监听资源通道

        Args:
            body: 包含通道信息的字典：
                {
                    'id': '监听通道ID',
                    'resourceId': '资源ID'
                }

        Returns:
            bool: 停止成功返回True

        Raises:
            HttpError: API调用失败
            Exception: 停止失败

        使用示例:
            >>> channels.stop({
            ...     'id': 'channel_id_123',
            ...     'resourceId': 'resource_id_456'
            ... })
        """
        try:
            self.service.stop(body=body).execute()
            return True
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"停止监听通道失败: {error_info}")

    @staticmethod
    def create_channel(channel_id: str, resource_uri: str,
                       webhook_url: str,
                       ttl_minutes: int = 60,
                       token: Optional[str] = None,
                       channel_type: str = 'web_hook') -> Dict[str, Any]:
        """
        创建监听通道的配置对象

        注意:
            这是辅助方法，用于创建通道配置对象
            实际的监听操作需要通过具体资源的watch方法完成

        Args:
            channel_id: 监听通道的唯一ID（建议使用UUID）
            resource_uri: 要监听的资源URI
            webhook_url: 接收通知的Webhook URL
            ttl_minutes: 通道令牌的TTL（分钟），默认60分钟
            token: 可选的令牌字符串，用于验证请求
            channel_type: 通道类型，目前仅支持 'web_hook'

        Returns:
            Dict: 通道配置对象

        使用示例:
            >>> channel_config = ChannelsService.create_channel(
            ...     channel_id='unique_channel_id',
            ...     resource_uri='https://www.googleapis.com/calendar/v3/calendars/primary/events',
            ...     webhook_url='https://example.com/webhook',
            ...     ttl_minutes=60
            ... )
            >>> # 然后使用 events_service.watch(channel_config)
        """
        body = {
            'id': channel_id,
            'resourceId': None,  # 这个会在watch时自动设置
            'resourceUri': resource_uri,
            'type': channel_type,
            'address': webhook_url,
            'params': {
                'ttl': str(ttl_minutes * 60 * 1000)  # 转换为毫秒
            }
        }

        if token:
            body['token'] = token

        return body

    @staticmethod
    def create_stop_config(channel_id: str, resource_id: str) -> Dict[str, Any]:
        """
        创建停止通道的配置对象

        Args:
            channel_id: 监听通道ID
            resource_id: 资源ID

        Returns:
            Dict: 停止通道配置对象

        使用示例:
            >>> stop_config = ChannelsService.create_stop_config(
            ...     channel_id='channel_id_123',
            ...     resource_id='resource_id_456'
            ... )
            >>> channels.stop(stop_config)
        """
        return {
            'id': channel_id,
            'resourceId': resource_id
        }
