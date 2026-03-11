"""
Google Calendar API 快速入门示例
最简单的上手方式
"""

from google_calendar_client import GoogleCalendarClient
from datetime import datetime, timedelta


def quickstart():
    """快速入门：5分钟上手 Google Calendar API"""

    print("="*60)
    print("Google Calendar API 快速入门")
    print("="*60)

    # 1. 初始化客户端
    print("\n[步骤1] 初始化客户端...")
    client = GoogleCalendarClient()
    print("✓ 客户端初始化成功")

    # 2. 创建一个简单事件
    print("\n[步骤2] 创建事件...")
    event = client.events.insert(
        summary='我的第一个事件',
        start=datetime.now() + timedelta(hours=1),
        end=datetime.now() + timedelta(hours=2),
        description='通过 Google Calendar API 创建的第一个事件'
    )
    print(f"✓ 事件创建成功，ID: {event['id']}")
    print(f"  标题: {event['summary']}")
    print(f"  开始时间: {event['start']['dateTime']}")

    # 3. 查询事件列表
    print("\n[步骤3] 查询未来7天的事件...")
    now = datetime.now()
    events = client.events.list(
        calendar_id='primary',
        time_min=now,
        time_max=now + timedelta(days=7),
        max_results=10
    )
    print(f"✓ 找到 {len(events)} 个事件:")
    for i, event in enumerate(events, 1):
        print(f"  {i}. {event['summary']}")

    # 4. 更新事件
    print("\n[步骤4] 更新事件...")
    updated_event = client.events.patch(
        event_id=event['id'],
        summary='已更新的标题'
    )
    print(f"✓ 事件更新成功，新标题: {updated_event['summary']}")

    # 5. 查询忙闲状态
    print("\n[步骤5] 查询今日忙闲状态...")
    start_of_day = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=18, minute=0, second=0, microsecond=0)

    busy_result = client.freebusy.query(
        time_min=start_of_day,
        time_max=end_of_day,
        calendar_ids=['primary']
    )

    busy_times = busy_result['calendars']['primary']['busy']
    print(f"✓ 今日9:00-18:00有 {len(busy_times)} 个忙碌时间段")

    # 6. 查询日历列表
    print("\n[步骤6] 查询我的日历列表...")
    calendars = client.calendar_list.list(min_access_role='reader')
    print(f"✓ 找到 {len(calendars)} 个日历:")
    for cal in calendars:
        if cal.get('primary'):
            print(f"  * {cal['summary']} (主日历)")
        else:
            print(f"  - {cal['summary']}")

    print("\n" + "="*60)
    print("快速入门完成！")
    print("="*60)
    print("\n接下来你可以：")
    print("1. 阅读 README.md 了解所有API接口")
    print("2. 运行 examples.py 查看更多示例")
    print("3. 根据需求修改 config.py 配置")
    print("4. 集成到你的项目中")


if __name__ == '__main__':
    try:
        quickstart()
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        print("\n请确保：")
        print("1. 已安装依赖: pip install -r requirements.txt")
        print("2. 已配置 client_secret.json 文件")
        print("3. 已完成首次 OAuth 认证")
        print("\n详细安装说明请参考 INSTALL.md")
