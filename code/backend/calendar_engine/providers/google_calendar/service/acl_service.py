"""
Google Calendar API - 访问控制列表资源 (Acl) 操作接口
"""

from typing import Dict, Any, Optional, List
from googleapiclient.errors import HttpError

from calendar_engine.providers.google_calendar.core.base_client import GoogleCalendarBaseClient
from calendar_engine.providers.google_calendar.core.config import MAX_RESULTS


class AclService:
    """访问控制列表资源操作服务"""

    def __init__(self, client: GoogleCalendarBaseClient):
        """
        初始化ACL服务

        Args:
            client: Google Calendar 基础客户端实例
        """
        self.client = client
        self.service = client.get_service().acl()

    def list(self, calendar_id: str = 'primary',
             max_results: int = MAX_RESULTS,
             page_token: Optional[str] = None,
             sync_token: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        返回日历的访问控制列表中的所有规则

        Args:
            calendar_id: 日历ID，默认为主日历
            max_results: 最大结果数
            page_token: 分页令牌
            sync_token: 同步令牌（用于增量同步）

        Returns:
            List[Dict]: ACL规则列表，每个规则包含：
                - kind: 资源类型 ("calendar#aclRule")
                - etag: ETag
                - id: 规则的唯一标识符
                - scope: 范围信息
                    - type: 范围类型（'default', 'user', 'group', 'domain'）
                    - value: 范围值（用户邮箱、组邮箱、域名等）
                - role: 权限角色
                    - 'none': 不提供任何访问权限
                    - 'freeBusyReader': 忙闲信息读取权限
                    - 'reader': 读取权限（隐藏私人事件详情）
                    - 'writer': 读写权限
                    - 'owner': 管理员权限

        Raises:
            HttpError: API调用失败
            Exception: 查询失败
        """
        params = {
            'calendarId': calendar_id,
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
            raise Exception(f"获取ACL列表失败: {error_info}")

    def get(self, rule_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        返回一条访问控制规则

        Args:
            rule_id: ACL规则ID
            calendar_id: 日历ID，默认为主日历

        Returns:
            Dict: ACL规则信息

        Raises:
            HttpError: API调用失败
            Exception: 获取失败
        """
        try:
            response = self.service.get(
                calendarId=calendar_id,
                ruleId=rule_id
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取ACL规则失败: {error_info}")

    def insert(self, scope_type: str, role: str,
               calendar_id: str = 'primary',
               scope_value: Optional[str] = None,
               send_notifications: bool = True
        ) -> Dict[str, Any]:
        """
        创建一条访问控制规则

        Args:
            scope_type: 范围类型
                - 'default': 公开范围
                - 'user': 单个用户
                - 'group': 组
                - 'domain': 域
            role: 权限角色
                - 'none': 无访问权限
                - 'freeBusyReader': 忙闲信息读取权限
                - 'reader': 读取权限
                - 'writer': 读写权限
                - 'owner': 管理员权限
            calendar_id: 日历ID，默认为主日历
            scope_value: 范围值（user或group时为邮箱，domain时为域名，default时省略）
            send_notifications: 是否发送通知
            send_updates: 更新通知方式（'none', 'externalOnly', 'all'）

        Returns:
            Dict: 新创建的ACL规则信息

        Raises:
            HttpError: API调用失败
            Exception: 创建失败
        """
        body = {
            'scope': {
                'type': scope_type
            },
            'role': role
        }

        if scope_value and scope_type != 'default':
            body['scope']['value'] = scope_value

        params = {
            'calendarId': calendar_id,
            'body': body,
            'sendNotifications': send_notifications,
            # 'sendUpdates': send_updates
        }

        try:
            response = self.service.insert(**params).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"创建ACL规则失败: {error_info}")

    def update(self, rule_id: str, scope_type: str, role: str,
               calendar_id: str = 'primary',
               scope_value: Optional[str] = None) -> Dict[str, Any]:
        """
        更新一条访问控制规则（完全替换）

        Args:
            rule_id: ACL规则ID
            scope_type: 范围类型
            role: 权限角色
            calendar_id: 日历ID
            scope_value: 范围值

        Returns:
            Dict: 更新后的ACL规则信息

        Raises:
            HttpError: API调用失败
            Exception: 更新失败
        """
        # 先获取当前规则
        try:
            rule = self.service.get(
                calendarId=calendar_id,
                ruleId=rule_id
            ).execute()
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"获取ACL规则失败: {error_info}")

        # 更新字段
        rule['scope'] = {
            'type': scope_type
        }
        if scope_value and scope_type != 'default':
            rule['scope']['value'] = scope_value
        rule['role'] = role

        try:
            response = self.service.update(
                calendarId=calendar_id,
                ruleId=rule_id,
                body=rule
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"更新ACL规则失败: {error_info}")

    def patch(self, rule_id: str, calendar_id: str = 'primary',
              **kwargs) -> Dict[str, Any]:
        """
        部分更新访问控制规则（补丁语义）

        注意:
            每个patch请求会消耗3个配额单位，建议先get再update

        Args:
            rule_id: ACL规则ID
            calendar_id: 日历ID
            **kwargs: 要更新的字段

        Returns:
            Dict: 更新后的ACL规则信息

        Raises:
            HttpError: API调用失败
            Exception: 更新失败
        """
        try:
            response = self.service.patch(
                calendarId=calendar_id,
                ruleId=rule_id,
                body=kwargs
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"部分更新ACL规则失败: {error_info}")

    def delete(self, rule_id: str, calendar_id: str = 'primary') -> bool:
        """
        删除一条访问控制规则

        Args:
            rule_id: ACL规则ID
            calendar_id: 日历ID，默认为主日历

        Returns:
            bool: 删除成功返回True

        Raises:
            HttpError: API调用失败
            Exception: 删除失败
        """
        try:
            self.service.delete(
                calendarId=calendar_id,
                ruleId=rule_id
            ).execute()
            return True
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"删除ACL规则失败: {error_info}")

    def watch(self, calendar_id: str = 'primary',
              body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        监听ACL资源的更改

        Args:
            calendar_id: 日历ID
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
            Dict: 监听响应

        Raises:
            HttpError: API调用失败
            Exception: 监听失败
        """
        if body is None:
            raise ValueError("body参数不能为空")

        try:
            response = self.service.watch(
                calendarId=calendar_id,
                body=body
            ).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"监听ACL失败: {error_info}")
