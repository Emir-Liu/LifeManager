"""
Google Calendar API 基础客户端
"""

import os
import json
import uuid

from datetime import datetime, timedelta, timezone

from typing import Optional, List, Dict, Any


from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


from calendar_engine.providers.google_calendar.core.config import (
    SCOPES,
    CREDENTIALS_FILE,
    CLIENT_SECRET_FILE,
    TIMEZONE,
    MAX_RESULTS,
)


class GoogleCalendarBaseClient:
    """Google Calendar API 基础客户端类"""


    # Web application 类型的固定配置
    REDIRECT_URI = 'http://localhost:5000/'
    OAUTH_PORT = 5000

    def __init__(self, credentials_file: str = CLIENT_SECRET_FILE,
                 token_file: str = CREDENTIALS_FILE):
        """
        初始化 Google Calendar API 客户端

        Args:
            credentials_file: OAuth 客户端密钥文件路径
            token_file: 存储的凭据文件路径
        """
        self.credentials = self._get_credentials(credentials_file, token_file)
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def _get_credentials(self, credentials_file: str, token_file: str) -> Credentials:
        """
        获取或刷新 Google OAuth 2.0 凭证

        Args:
            credentials_file: OAuth 客户端密钥文件路径
            token_file: 存储的凭据文件路径

        Returns:
            Credentials: Google OAuth 2.0 凭证对象
        """
        creds = None

        # 尝试从文件加载现有的凭证
        if os.path.exists(token_file):
            with open(token_file, 'r') as token:
                creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)

        # 如果凭证不存在或过期，则获取新凭证
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # 刷新过期的凭证
                creds.refresh(Request())
            else:
                # 创建新的凭证流程
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            # 保存凭证供下次使用
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
                print(f'保存tokens:{token_file}')

        return creds

    def _format_datetime(self, dt: datetime) -> str:
        """
        格式化日期时间为 Google Calendar API 需要的格式

        Args:
            dt: datetime 对象

        Returns:
            str: 格式化后的日期时间字符串 (RFC3339)
        """
        # 确保 datetime 有时区信息
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # 格式化为 RFC3339 格式，确保时区有冒号
        formatted = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        # 在时区偏移量中插入冒号: +0900 -> +09:00
        if len(formatted) > 5 and formatted[-5] in '+-':
            formatted = formatted[:-2] + ':' + formatted[-2:]
        return formatted

    def _format_date(self, dt: datetime) -> str:
        """
        格式化日期为 Google Calendar API 需要的格式

        Args:
            dt: datetime 对象

        Returns:
            str: 格式化后的日期字符串
        """
        return dt.strftime('%Y-%m-%d')

    def _handle_error(self, error: HttpError) -> Dict[str, Any]:
        """
        处理 API 错误

        Args:
            error: HttpError 对象

        Returns:
            Dict: 错误信息字典
        """
        error_info = {
            'status_code': error.resp.status,
            'error_reason': error.reason,
            'error_details': error.error_details
        }
        return error_info

    def get_service(self):
        """
        获取 Google Calendar API 服务对象

        Returns:
            Resource: Google Calendar API 服务对象
        """
        return self.service

    def get_quota_status(self) -> Dict[str, Any]:
        """
        获取当前配额状态（需要从 API 响应中获取）

        Returns:
            Dict: 配额状态信息
        """
        # 注意：这个方法需要在实际 API 调用中从响应头获取配额信息
        return {
            'message': '配额信息需要从实际 API 调用的响应头中获取',
            'max_results_per_day': 10000,
            'quota_used': '未知'
        }
