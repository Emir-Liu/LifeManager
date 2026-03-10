"""
Google Calendar API - 忙闲查询资源 (Freebusy) 操作接口
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from googleapiclient.errors import HttpError

from core.base_client import GoogleCalendarBaseClient


class FreebusyService:
    """忙闲查询资源操作服务"""

    def __init__(self, client: GoogleCalendarBaseClient):
        """
        初始化忙闲查询服务

        Args:
            client: Google Calendar 基础客户端实例
        """
        self.client = client
        self.service = client.get_service().freebusy()

    def query(self, time_min: datetime, time_max: datetime,
              calendar_ids: List[str],
              group_expansion_max: int = 10,
              calendar_expansion_max: int = 50) -> Dict[str, Any]:
        """
        查询一组日历的空闲/忙碌信息

        Args:
            time_min: 查询开始时间（datetime对象）
            time_max: 查询结束时间（datetime对象）
            calendar_ids: 日历ID列表（如 ['primary', 'user@example.com']）
            group_expansion_max: 组扩展的最大数量（默认10）
            calendar_expansion_max: 日历扩展的最大数量（默认50）

        Returns:
            Dict: 忙闲信息，包含：
                - timeMin: 查询开始时间
                - timeMax: 查询结束时间
                - calendars: 字典，键为日历ID，值为该日历的忙闲信息：
                    - busy: 忙碌时间区间列表
                        {
                            'start': 'RFC3339格式时间',
                            'end': 'RFC3339格式时间'
                        }
                    - errors: 错误信息（如果有）
                - groups: 字典，键为组ID，值为该组的日历ID列表
                - calendarExpansionMax: 请求的最大日历扩展数

        Raises:
            HttpError: API调用失败
            Exception: 查询失败

        使用示例:
            >>> time_min = datetime(2025, 3, 1, 0, 0, 0)
            >>> time_max = datetime(2025, 3, 2, 0, 0, 0)
            >>> result = freebusy.query(time_min, time_max, ['primary'])
            >>> busy_times = result['calendars']['primary']['busy']
        """
        body = {
            'timeMin': self.client._format_datetime(time_min),
            'timeMax': self.client._format_datetime(time_max),
            'items': [{'id': cal_id} for cal_id in calendar_ids],
            'groupExpansionMax': group_expansion_max,
            'calendarExpansionMax': calendar_expansion_max
        }

        try:
            response = self.service.query(body=body).execute()
            return response
        except HttpError as error:
            error_info = self.client._handle_error(error)
            raise Exception(f"查询忙闲信息失败: {error_info}")

    def find_free_time(self, time_min: datetime, time_max: datetime,
                       calendar_ids: List[str],
                       duration_minutes: int = 60,
                       min_gap_minutes: int = 0) -> List[Dict[str, Any]]:
        """
        查找所有日历的共同空闲时间

        Args:
            time_min: 查询开始时间
            time_max: 查询结束时间
            calendar_ids: 日历ID列表
            duration_minutes: 需要的最小持续时间（分钟）
            min_gap_minutes: 时间段之间的最小间隔（分钟）

        Returns:
            List[Dict]: 空闲时间段列表，每个时间段包含：
                - start: 开始时间（RFC3339格式）
                - end: 结束时间（RFC3339格式）
                - duration_minutes: 持续时间（分钟）

        Raises:
            Exception: 查询失败
        """
        try:
            # 获取所有日历的忙闲信息
            busy_response = self.query(time_min, time_max, calendar_ids)

            # 合并所有日历的忙碌时间段
            all_busy = []
            for cal_id in calendar_ids:
                if cal_id in busy_response.get('calendars', {}):
                    calendar_busy = busy_response['calendars'][cal_id].get('busy', [])
                    for busy_slot in calendar_busy:
                        all_busy.append({
                            'start': datetime.fromisoformat(busy_slot['start'].replace('Z', '+00:00')),
                            'end': datetime.fromisoformat(busy_slot['end'].replace('Z', '+00:00'))
                        })

            # 按开始时间排序忙碌时间段
            all_busy.sort(key=lambda x: x['start'])

            # 合并重叠的忙碌时间段
            merged_busy = []
            for busy_slot in all_busy:
                if not merged_busy:
                    merged_busy.append(busy_slot)
                else:
                    last_busy = merged_busy[-1]
                    if busy_slot['start'] <= last_busy['end']:
                        # 重叠，合并
                        merged_busy[-1] = {
                            'start': last_busy['start'],
                            'end': max(last_busy['end'], busy_slot['end'])
                        }
                    else:
                        merged_busy.append(busy_slot)

            # 计算空闲时间段
            free_times = []
            current_time = time_min

            for busy_slot in merged_busy:
                if busy_slot['start'] > current_time:
                    # 在忙碌时间段之前有空闲
                    free_duration = (busy_slot['start'] - current_time).total_seconds() / 60
                    if free_duration >= duration_minutes:
                        free_times.append({
                            'start': self.client._format_datetime(current_time),
                            'end': self.client._format_datetime(busy_slot['start']),
                            'duration_minutes': int(free_duration)
                        })
                # 移动到忙碌时间段结束之后
                current_time = max(current_time, busy_slot['end'])

            # 检查最后一个忙碌时间段之后是否有空闲
            if time_max > current_time:
                free_duration = (time_max - current_time).total_seconds() / 60
                if free_duration >= duration_minutes:
                    free_times.append({
                        'start': self.client._format_datetime(current_time),
                        'end': self.client._format_datetime(time_max),
                        'duration_minutes': int(free_duration)
                    })

            # 根据最小间隔过滤
            if min_gap_minutes > 0:
                filtered_free_times = []
                for i, free_time in enumerate(free_times):
                    if i == 0:
                        filtered_free_times.append(free_time)
                    else:
                        prev_free = filtered_free_times[-1]
                        prev_end = datetime.fromisoformat(prev_free['end'].replace('Z', '+00:00'))
                        curr_start = datetime.fromisoformat(free_time['start'].replace('Z', '+00:00'))
                        gap = (curr_start - prev_end).total_seconds() / 60
                        if gap >= min_gap_minutes:
                            filtered_free_times.append(free_time)
                return filtered_free_times

            return free_times

        except Exception as e:
            raise Exception(f"查找空闲时间失败: {str(e)}")

    def is_busy_at(self, calendar_id: str, time: datetime) -> bool:
        """
        检查指定日历在特定时间是否忙碌

        Args:
            calendar_id: 日历ID
            time: 要检查的时间点

        Returns:
            bool: 忙碌返回True，空闲返回False

        Raises:
            Exception: 查询失败
        """
        try:
            # 查询时间点前后1分钟
            time_min = time - timedelta(minutes=1)
            time_max = time + timedelta(minutes=1)

            busy_response = self.query(time_min, time_max, [calendar_id])

            # 检查该时间段内是否有忙碌记录
            calendar_busy = busy_response.get('calendars', {}).get(calendar_id, {}).get('busy', [])

            if calendar_busy:
                return True

            return False

        except Exception as e:
            raise Exception(f"检查忙闲状态失败: {str(e)}")
