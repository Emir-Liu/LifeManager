"""
Google Calendar API 使用示例集合
包含各种常见场景的完整代码示例
"""

from calendar_engine.providers.google_calendar.core.google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta


def example_1_create_simple_event():
    """示例1: 创建简单事件"""
    print("\n=== 示例1: 创建简单事件 ===")

    client = GoogleCalendarClient()

    event = client.events.insert(
        summary='团队会议',
        start=datetime.now() + timedelta(hours=1),
        end=datetime.now() + timedelta(hours=2),
        description='讨论项目进度'
    )

    print(f"事件创建成功!")
    print(f"ID: {event['id']}")
    print(f"标题: {event['summary']}")
    print(f"开始时间: {event['start']['dateTime']}")


def example_2_create_recurring_event():
    """示例2: 创建重复事件"""
    print("\n=== 示例2: 创建重复事件 ===")

    client = GoogleCalendarClient()

    event = client.events.insert(
        summary='每周例会',
        start=datetime(2025, 3, 10, 14, 0, 0),
        end=datetime(2025, 3, 10, 15, 0, 0),
        description='每周一团队例会',
        recurrence=['RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=10'],  # 每周一，重复10次
        reminders={
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24*60},  # 提前1天
                {'method': 'popup', 'minutes': 15}      # 提前15分钟
            ]
        }
    )

    print(f"重复事件创建成功!")
    print(f"ID: {event['id']}")
    print(f"重复规则: {event['recurrence']}")


def example_3_create_event_with_attendees():
    """示例3: 创建带参与者的会议"""
    print("\n=== 示例3: 创建带参与者的会议 ===")

    client = GoogleCalendarClient()

    event = client.events.insert(
        summary='项目启动会议',
        start=datetime.now() + timedelta(days=1, hours=10),
        end=datetime.now() + timedelta(days=1, hours=11),
        location='会议室A',
        description='讨论新项目启动计划',
        attendees=[
            {'email': 'user1@example.com', 'responseStatus': 'needsAction'},
            {'email': 'user2@example.com', 'responseStatus': 'needsAction'},
            {'email': 'user3@example.com', 'responseStatus': 'needsAction'}
        ],
        send_updates='all'  # 发送通知给所有参与者
    )

    print(f"会议创建成功!")
    print(f"参与者数量: {len(event['attendees'])}")
    for attendee in event['attendees']:
        print(f"  - {attendee['email']}: {attendee['responseStatus']}")


def example_4_list_events():
    """示例4: 查询事件列表"""
    print("\n=== 示例4: 查询事件列表 ===")

    client = GoogleCalendarClient()

    # 查询未来7天的事件
    now = datetime.now()
    events = client.events.list(
        calendar_id='primary',
        time_min=now,
        time_max=now + timedelta(days=7),
        order_by='startTime'
    )

    print(f"未来7天共有 {len(events)} 个事件:")
    for event in events:
        print(f"\n  标题: {event['summary']}")
        print(f"  开始: {event['start'].get('dateTime', event['start'].get('date'))}")
        print(f"  ID: {event['id']}")


def example_5_search_events():
    """示例5: 搜索事件"""
    print("\n=== 示例5: 搜索事件 ===")

    client = GoogleCalendarClient()

    # 搜索包含"会议"关键字的事件
    events = client.events.list(
        calendar_id='primary',
        q='会议',
        max_results=10
    )

    print(f"搜索到 {len(events)} 个包含'会议'的事件:")
    for event in events:
        print(f"  - {event['summary']}")


def example_6_update_event():
    """示例6: 更新事件"""
    print("\n=== 示例6: 更新事件 ===")

    client = GoogleCalendarClient()

    # 首先创建一个事件
    new_event = client.events.insert(
        summary='临时会议',
        start=datetime.now() + timedelta(hours=2),
        end=datetime.now() + timedelta(hours=3)
    )

    event_id = new_event['id']

    # 更新事件
    updated_event = client.events.patch(
        event_id=event_id,
        summary='已更新的会议',
        description='更新后的描述'
    )

    print(f"事件更新成功!")
    print(f"新标题: {updated_event['summary']}")
    print(f"新描述: {updated_event['description']}")


def example_7_delete_event():
    """示例7: 删除事件"""
    print("\n=== 示例7: 删除事件 ===")

    client = GoogleCalendarClient()

    # 首先创建一个事件
    new_event = client.events.insert(
        summary='待删除的事件',
        start=datetime.now() + timedelta(hours=4),
        end=datetime.now() + timedelta(hours=5)
    )

    event_id = new_event['id']
    print(f"创建事件: {event_id}")

    # 删除事件
    success = client.events.delete(event_id=event_id)
    if success:
        print("事件删除成功!")


def example_8_create_calendar():
    """示例8: 创建日历"""
    print("\n=== 示例8: 创建日历 ===")

    client = GoogleCalendarClient()

    calendar = client.calendars.insert(
        summary='工作日历',
        description='用于工作安排的日历',
        location='北京',
        time_zone='Asia/Shanghai'
    )

    print(f"日历创建成功!")
    print(f"ID: {calendar['id']}")
    print(f"标题: {calendar['summary']}")


def example_9_list_calendars():
    """示例9: 查询日历列表"""
    print("\n=== 示例9: 查询日历列表 ===")

    client = GoogleCalendarClient()

    calendars = client.calendar_list.list(
        min_access_role='reader'
    )

    print(f"找到 {len(calendars)} 个日历:")
    for cal in calendars:
        print(f"\n  标题: {cal['summary']}")
        print(f"  ID: {cal['id']}")
        print(f"  访问权限: {cal['accessRole']}")
        print(f"  是否主日历: {cal.get('primary', False)}")


def example_10_freebusy_query():
    """示例10: 查询忙闲状态"""
    print("\n=== 示例10: 查询忙闲状态 ===")

    client = GoogleCalendarClient()

    # 查询今天9点到18点的忙闲状态
    now = datetime.now()
    start_of_day = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=18, minute=0, second=0, microsecond=0)

    result = client.freebusy.query(
        time_min=start_of_day,
        time_max=end_of_day,
        calendar_ids=['primary']
    )

    busy_times = result['calendars']['primary']['busy']
    print(f"今天9:00-18:00共有 {len(busy_times)} 个忙碌时间段:")
    for busy in busy_times:
        start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
        duration = (end - start).total_seconds() / 60
        print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')} ({int(duration)} 分钟)")


def example_11_find_free_time():
    """示例11: 查找共同空闲时间"""
    print("\n=== 示例11: 查找共同空闲时间 ===")

    client = GoogleCalendarClient()

    # 查找明天9点到18点的1小时空闲时间段
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)

    free_times = client.freebusy.find_free_time(
        time_min=start_time,
        time_max=end_time,
        calendar_ids=['primary'],
        duration_minutes=60
    )

    print(f"找到 {len(free_times)} 个1小时以上的空闲时间段:")
    for free in free_times:
        start = datetime.fromisoformat(free['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(free['end'].replace('Z', '+00:00'))
        print(f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')} ({free['duration_minutes']} 分钟)")


def example_12_quick_add():
    """示例12: 快速创建事件"""
    print("\n=== 示例12: 快速创建事件 ===")

    client = GoogleCalendarClient()

    event = client.events.quick_add(
        text='明天下午3点开会',
        calendar_id='primary'
    )

    print(f"快速创建事件成功!")
    print(f"标题: {event['summary']}")
    print(f"开始时间: {event['start'].get('dateTime', event['start'].get('date'))}")


def example_13_move_event():
    """示例13: 移动事件到其他日历"""
    print("\n=== 示例13: 移动事件到其他日历 ===")

    client = GoogleCalendarClient()

    # 创建一个次级日历
    new_calendar = client.calendars.insert(summary='测试日历')
    target_calendar_id = new_calendar['id']

    # 在主日历创建一个事件
    event = client.events.insert(
        summary='待移动的事件',
        start=datetime.now() + timedelta(hours=5),
        end=datetime.now() + timedelta(hours=6)
    )

    event_id = event['id']
    print(f"在主日历创建事件: {event_id}")

    # 移动到其他日历
    moved_event = client.events.move(
        event_id=event_id,
        destination_calendar_id=target_calendar_id
    )

    print(f"事件已移动到日历: {target_calendar_id}")


def example_14_share_calendar():
    """示例14: 共享日历"""
    print("\n=== 示例14: 共享日历 ===")

    client = GoogleCalendarClient()

    # 给用户读取权限
    rule = client.acl.insert(
        scope_type='user',
        role='reader',
        scope_value='user@example.com',
        send_notifications=True
    )

    print(f"已共享日历给用户: user@example.com")
    print(f"权限: {rule['role']}")
    print(f"规则ID: {rule['id']}")


def example_15_list_acl():
    """示例15: 查询访问控制列表"""
    print("\n=== 示例15: 查询访问控制列表 ===")

    client = GoogleCalendarClient()

    acl_rules = client.acl.list(calendar_id='primary')

    print(f"主日历共有 {len(acl_rules)} 个访问规则:")
    for rule in acl_rules:
        scope_type = rule['scope']['type']
        scope_value = rule['scope'].get('value', '')
        role = rule['role']
        print(f"  权限: {role:15} - 范围: {scope_type:10} {scope_value}")


def example_16_get_settings():
    """示例16: 获取用户设置"""
    print("\n=== 示例16: 获取用户设置 ===")

    client = GoogleCalendarClient()

    # 获取所有设置
    all_settings = client.settings.get_all_settings_dict()

    print("用户设置:")
    for key, value in all_settings.items():
        print(f"  {key}: {value}")

    # 获取特定设置
    timezone = client.settings.get_timezone()
    locale = client.settings.get_locale()
    week_start = client.settings.get_week_start()

    print(f"\n时区: {timezone}")
    print(f"区域设置: {locale}")
    print(f"一周开始日: {week_start} (0=周日, 1=周一)")


def example_17_error_handling():
    """示例17: 错误处理"""
    print("\n=== 示例17: 错误处理 ===")

    client = GoogleCalendarClient()

    try:
        # 尝试获取不存在的事件
        event = client.events.get('non_existent_event_id')
    except Exception as e:
        print(f"捕获到错误: {str(e)}")

    try:
        # 尝试创建不合法的事件
        event = client.events.insert(
            summary='测试事件',
            start=datetime.now(),
            end=datetime.now() - timedelta(hours=1)  # 结束时间早于开始时间
        )
    except Exception as e:
        print(f"捕获到错误: {str(e)}")


def example_18_get_recurring_event_instances():
    """示例18: 获取重复事件实例"""
    print("\n=== 示例18: 获取重复事件实例 ===")

    client = GoogleCalendarClient()

    # 首先创建一个重复事件
    event = client.events.insert(
        summary='每周例会',
        start=datetime(2025, 3, 10, 14, 0, 0),
        end=datetime(2025, 3, 10, 15, 0, 0),
        recurrence=['RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=5']  # 每周一，重复5次
    )

    event_id = event['id']

    # 获取所有实例
    instances = client.events.instances(
        event_id=event_id,
        calendar_id='primary'
    )

    print(f"重复事件共有 {len(instances)} 个实例:")
    for instance in instances:
        print(f"  {instance['start']['dateTime']} - {instance['end']['dateTime']}")


def example_19_update_calendar_list():
    """示例19: 更新日历列表显示属性"""
    print("\n=== 示例19: 更新日历列表显示属性 ===")

    client = GoogleCalendarClient()

    # 创建一个次级日历
    new_calendar = client.calendars.insert(summary='测试日历')
    calendar_id = new_calendar['id']

    # 更新日历在列表中的显示属性
    updated_calendar = client.calendar_list.patch(
        calendar_id=calendar_id,
        summary_override='自定义标题',
        color_id='2',
        selected=True
    )

    print(f"日历列表属性更新成功!")
    # print(f"自定义标题: {updated_calendar['summaryOverride']}")
    print(f"自定义标题: {updated_calendar.get('summaryOverride', '未设置')}")
    print(f"颜色ID: {updated_calendar['colorId']}")


def example_20_calendar_operations():
    """示例20: 完整的日历操作流程"""
    print("\n=== 示例20: 完整的日历操作流程 ===")

    client = GoogleCalendarClient()

    # 1. 创建日历
    calendar = client.calendars.insert(
        summary='项目日历',
        description='用于项目管理的日历',
        time_zone='Asia/Shanghai'
    )
    print(f"1. 创建日历: {calendar['id']}")

    # 2. 在日历中创建事件
    event = client.events.insert(
        summary='项目启动会议',
        start=datetime.now() + timedelta(hours=6),
        end=datetime.now() + timedelta(hours=7),
        calendar_id=calendar['id'],
        description='项目启动会议'
    )
    print(f"2. 创建事件: {event['id']}")

    # 3. 更新日历属性
    updated_calendar = client.calendars.patch(
        calendar_id=calendar['id'],
        summary='项目管理日历'
    )
    print(f"3. 更新日历标题: {updated_calendar['summary']}")

    # 4. 查询日历中的事件
    events = client.events.list(calendar_id=calendar['id'])
    print(f"4. 日历中共有 {len(events)} 个事件")


def run_all_examples():
    """运行所有示例"""
    print("\n" + "="*50)
    print("Google Calendar API 使用示例集合")
    print("="*50)

    examples = [
        example_1_create_simple_event,
        example_2_create_recurring_event,
        example_3_create_event_with_attendees,
        example_4_list_events,
        example_5_search_events,
        example_6_update_event,
        example_7_delete_event,
        example_8_create_calendar,
        example_9_list_calendars,
        example_10_freebusy_query,
        example_11_find_free_time,
        example_12_quick_add,
        example_13_move_event,
        example_14_share_calendar,
        example_15_list_acl,
        example_16_get_settings,
        example_17_error_handling,
        example_18_get_recurring_event_instances,
        example_19_update_calendar_list,
        example_20_calendar_operations
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n示例执行失败: {str(e)}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*50)
    print("所有示例执行完成!")
    print("="*50)


if __name__ == '__main__':
    # 运行所有示例
    run_all_examples()

    # 或者运行单个示例
    # example_1_create_simple_event()
    # example_2_create_recurring_event()
    # example_3_create_event_with_attendees()
    # example_4_list_events()
