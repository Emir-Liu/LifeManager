import os
import glob
from dotenv import load_dotenv
from langchain.tools import tool
from calendar_engine.core.factory import CalendarProviderFactory
from calendar_engine.core.manager import CalendarManager
from calendar_engine.core.models import Event

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))


# 获取 Google Calendar 凭证路径
def _get_google_calendar_config():
    """从环境变量获取 Google Calendar 配置"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # 从环境变量获取配置路径
    credentials_pattern = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH',
                                   'calendar_engine/providers/google_calendar/service/desktop_client_secret_*.json')
    token_path_env = os.getenv('GOOGLE_CALENDAR_TOKEN_PATH',
                              'calendar_engine/providers/google_calendar/service/token.json')

    # 解析 credentials 路径（支持通配符）
    credentials_path_pattern = os.path.join(base_dir, credentials_pattern)
    credentials_files = glob.glob(credentials_path_pattern)
    credentials_path = credentials_files[0] if credentials_files else None

    # 解析 token 路径
    token_path = os.path.join(base_dir, token_path_env)

    if not credentials_path:
        raise ValueError(
            f"未找到 Google Calendar credentials 文件: {credentials_path_pattern}\n"
            f"请确保在 .env 中配置正确的 GOOGLE_CALENDAR_CREDENTIALS_PATH"
        )

    return {
        'credentials_path': credentials_path,
        'token_path': token_path
    }


# 获取提供者实例
def _get_provider(provider: str):
    """获取日历提供者实例"""
    factory = CalendarProviderFactory()

    if provider == 'google':
        config = _get_google_calendar_config()
        return factory.create(provider, config)
    else:
        # 其他提供者可能不需要特殊配置
        return factory.create(provider)

@tool
def list_events(provider: str = "google", calendar_id: str = "primary",
               start_time: str = None, end_time: str = None):
    """查询事件列表

    Args:
        provider: 日历提供者 (google/outlook/apple)
        calendar_id: 日历ID
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)

    Returns:
        事件列表
    """
    print(f'调用工具：查询事件列表')

    provider_instance = _get_provider(provider)
    return provider_instance.list_events(calendar_id, start_time, end_time)


@tool
def create_event(provider: str, calendar_id: str, summary: str, start_time: str,
                end_time: str, description: str = ""):
    """创建新事件

    Args:
        provider: 日历提供者
        calendar_id: 日历ID
        summary: 事件标题
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
        description: 事件描述

    Returns:
        创建的事件
    """
    print(f'调用工具：创建新事件')

    provider_instance = _get_provider(provider)

    event = Event(
        id="",
        calendar_id=calendar_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description
    )

    return provider_instance.create_event(calendar_id, event)


@tool
def update_event(provider: str, event_id: str, calendar_id: str,
                summary: str = None, start_time: str = None,
                end_time: str = None, description: str = None):
    """更新事件

    Args:
        provider: 日历提供者
        event_id: 事件ID
        calendar_id: 日历ID
        summary: 事件标题
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
        description: 事件描述

    Returns:
        更新后的事件
    """
    print(f'调用工具：更新事件')

    provider_instance = _get_provider(provider)

    event = Event(
        id=event_id,
        calendar_id=calendar_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description
    )

    return provider_instance.update_event(event_id, event)


@tool
def delete_event(provider: str, event_id: str, calendar_id: str = "primary"):
    """删除事件

    Args:
        provider: 日历提供者
        event_id: 事件ID
        calendar_id: 日历ID（默认为 primary，从事件列表中获取）

    Returns:
        是否删除成功
    """
    print(f'调用工具：删除事件 (ID: {event_id}, Calendar: {calendar_id})')

    provider_instance = _get_provider(provider)
    return provider_instance.delete_event(event_id, calendar_id)


@tool
def get_event(provider: str, event_id: str):
    """查询事件详情

    Args:
        provider: 日历提供者
        event_id: 事件ID

    Returns:
        事件详情
    """
    print(f'调用工具：查询事件详情')

    provider_instance = _get_provider(provider)
    return provider_instance.get_event(event_id)


@tool
def list_calendars(provider: str = "google"):
    """查询日历列表

    Args:
        provider: 日历提供者

    Returns:
        日历列表
    """
    print(f'调用工具：查询日历列表')

    provider_instance = _get_provider(provider)
    return provider_instance.list_calendars()


@tool
def sync_event(summary: str, start_time: str, end_time: str,
               targets: list, calendar_id: str = "primary"):
    """跨日历同步事件

    Args:
        summary: 事件标题
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
        targets: 目标日历提供者列表,如 ["google", "outlook"]
        calendar_id: 目标日历ID

    Returns:
        同步成功的事件列表
    """
    print(f'调用工具：跨日历同步事件')

    event = Event(
        id="",
        calendar_id=calendar_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time
    )

    synced_events = []
    for provider_name in targets:
        provider_instance = _get_provider(provider_name)
        result = provider_instance.create_event(calendar_id, event)
        synced_events.append(result)

    return synced_events


@tool
def list_all_events(start_time: str, end_time: str):
    """聚合查询所有日历的事件

    Args:
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)

    Returns:
        所有日历的事件列表(按时间排序)
    """
    print(f'调用工具：聚合查询所有日历的事件')

    factory = CalendarProviderFactory()

    # 创建所有已注册的提供者实例
    providers = {}
    for provider_type in factory.list_providers():
        try:
            providers[provider_type] = _get_provider(provider_type)
        except Exception as e:
            print(f"创建 {provider_type} 提供者失败: {e}")
            continue

    # 创建 CalendarManager 并查询所有事件
    manager = CalendarManager(providers=providers)
    return manager.list_all_events(start_time, end_time)


@tool
def clear_calendar(provider: str = "google", calendar_id: str = "primary"):
    """清空日历（删除所有事件）

    Args:
        provider: 日历提供者
        calendar_id: 日历ID

    Returns:
        是否清空成功
    """
    print(f'调用工具：清空日历')
    provider_instance = _get_provider(provider)
    return provider_instance.clear_calendar(calendar_id)


@tool
def delete_calendar(provider: str, calendar_id: str):
    """删除日历

    Args:
        provider: 日历提供者
        calendar_id: 日历ID

    Returns:
        是否删除成功
    """
    print(f'调用工具：删除日历')
    provider_instance = _get_provider(provider)
    return provider_instance.delete_calendar(calendar_id)


@tool
def create_calendar(provider: str, summary: str, description: str = ""):
    """创建新日历

    Args:
        provider: 日历提供者
        summary: 日历标题
        description: 日历描述

    Returns:
        创建的日历
    """
    print(f'调用工具：创建新日历')
    provider_instance = _get_provider(provider)
    return provider_instance.create_calendar(summary, description)


@tool
def get_calendar_details(provider: str, calendar_id: str):
    """获取日历详情

    Args:
        provider: 日历提供者
        calendar_id: 日历ID

    Returns:
        日历详情
    """
    print(f'调用工具：获取日历详情')
    provider_instance = _get_provider(provider)
    return provider_instance.get_calendar(calendar_id)


@tool
def update_calendar(provider: str, calendar_id: str, summary: str = None,
                description: str = None, location: str = None):
    """更新日历信息

    Args:
        provider: 日历提供者
        calendar_id: 日历ID
        summary: 日历标题
        description: 日历描述
        location: 日历位置

    Returns:
        更新后的日历
    """
    print(f'调用工具：更新日历信息')
    provider_instance = _get_provider(provider)
    return provider_instance.update_calendar(calendar_id, summary, description, location)


@tool
def list_recurring_events(provider: str = "google", calendar_id: str = "primary",
                        start_time: str = None, end_time: str = None):
    """查询重复事件列表

    Args:
        provider: 日历提供者
        calendar_id: 日历ID
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)

    Returns:
        重复事件列表
    """
    print(f'调用工具：查询重复事件列表')
    provider_instance = _get_provider(provider)
    return provider_instance.list_recurring_events(calendar_id, start_time, end_time)


@tool
def create_recurring_event(provider: str, calendar_id: str, summary: str, start_time: str,
                          end_time: str, recurrence_rule: str, description: str = ""):
    """创建重复事件

    Args:
        provider: 日历提供者
        calendar_id: 日历ID
        summary: 事件标题
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
        recurrence_rule: 重复规则 (RRULE格式，如 "FREQ=WEEKLY;COUNT=10" 或 "FREQ=DAILY;UNTIL=2024-12-31")
        description: 事件描述

    Returns:
        创建的重复事件

    重复规则示例:
        - "FREQ=DAILY;COUNT=10" - 每天重复10次
        - "FREQ=WEEKLY;BYDAY=MO,WE,FR" - 每周一、三、五重复
        - "FREQ=MONTHLY;BYMONTHDAY=15" - 每月15日重复
        - "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25" - 每年12月25日重复
        - "FREQ=WEEKLY;UNTIL=2024-12-31" - 每周重复直到2024年12月31日
    """
    print(f'调用工具：创建重复事件')
    provider_instance = _get_provider(provider)

    event = Event(
        id="",
        calendar_id=calendar_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description
    )

    return provider_instance.create_recurring_event(calendar_id, event, recurrence_rule)


@tool
def update_recurring_event(provider: str, event_id: str, calendar_id: str,
                            summary: str = None, start_time: str = None,
                            end_time: str = None, description: str = None,
                            update_scope: str = "future"):
    """更新重复事件

    Args:
        provider: 日历提供者
        event_id: 事件ID
        calendar_id: 日历ID
        summary: 事件标题
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
        description: 事件描述
        update_scope: 更新范围
            - "future": 更新此实例及所有未来实例 (默认)
            - "all": 更新所有实例
            - "single": 只更新此实例

    Returns:
        更新后的事件
    """
    print(f'调用工具：更新重复事件')
    provider_instance = _get_provider(provider)

    event = Event(
        id=event_id,
        calendar_id=calendar_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description
    )

    return provider_instance.update_recurring_event(event_id, calendar_id, event, update_scope)


@tool
def delete_recurring_event(provider: str, event_id: str, calendar_id: str,
                           delete_scope: str = "future"):
    """删除重复事件

    Args:
        provider: 日历提供者
        event_id: 事件ID
        calendar_id: 日历ID
        delete_scope: 删除范围
            - "future": 删除此实例及所有未来实例 (默认)
            - "all": 删除所有实例
            - "single": 只删除此实例

    Returns:
        是否删除成功
    """
    print(f'调用工具：删除重复事件')
    provider_instance = _get_provider(provider)
    return provider_instance.delete_recurring_event(event_id, calendar_id, delete_scope)


@tool
def get_recurring_event_instances(provider: str, event_id: str, calendar_id: str):
    """获取重复事件的所有实例

    Args:
        provider: 日历提供者
        event_id: 重复事件ID
        calendar_id: 日历ID

    Returns:
        重复事件实例列表
    """
    print(f'调用工具：获取重复事件的所有实例')
    provider_instance = _get_provider(provider)
    return provider_instance.get_recurring_event_instances(event_id, calendar_id)
