"""Google Calendar Calendars 服务封装"""

from googleapiclient.errors import HttpError


class CalendarsService:
    """Google Calendar API 的 Calendars 服务封装"""

    def __init__(self, client):
        """初始化服务

        Args:
            client: GoogleCalendarBaseClient 实例
        """
        self.client = client
        self._service = client.service.calendars()

    def get(self, calendar_id: str) -> dict:
        """获取日历详情

        Args:
            calendar_id: 日历ID

        Returns:
            日历字典
        """
        try:
            result = self._service.get(calendarId=calendar_id).execute()
            return result
        except HttpError as e:
            print(f"获取日历失败: {e}")
            raise

    def insert(self, summary: str, description: str = None) -> dict:
        """创建新日历

        Args:
            summary: 日历标题
            description: 日历描述

        Returns:
            创建的日历字典
        """
        body = {'summary': summary}
        if description:
            body['description'] = description

        try:
            result = self._service.insert(body=body).execute()
            return result
        except HttpError as e:
            print(f"创建日历失败: {e}")
            raise

    def update(self, calendar_id: str, summary: str = None,
              description: str = None, location: str = None) -> dict:
        """更新日历信息

        Args:
            calendar_id: 日历ID
            summary: 日历标题
            description: 日历描述
            location: 日历位置

        Returns:
            更新后的日历字典
        """
        # 先获取当前日历信息
        calendar = self.get(calendar_id)

        body = {}
        if summary:
            body['summary'] = summary
        elif 'summary' in calendar:
            body['summary'] = calendar['summary']

        if description:
            body['description'] = description
        elif 'description' in calendar:
            body['description'] = calendar.get('description', '')

        if location:
            body['location'] = location
        elif 'location' in calendar:
            body['location'] = calendar.get('location', '')

        try:
            result = self._service.update(calendarId=calendar_id, body=body).execute()
            return result
        except HttpError as e:
            print(f"更新日历失败: {e}")
            raise

    def delete(self, calendar_id: str) -> bool:
        """删除日历

        Args:
            calendar_id: 日历ID

        Returns:
            是否删除成功
        """
        try:
            self._service.delete(calendarId=calendar_id).execute()
            return True
        except HttpError as e:
            print(f"删除日历失败: {e}")
            if e.resp.status == 404:
                # 日历不存在
                return True
            return False
