"""
Google Calendar API 配置文件
"""

# OAuth 2.0 认证范围
SCOPES = [
    'https://www.googleapis.com/auth/calendar',  # 完整的日历访问权限
    # 其他可选权限：
    # 'https://www.googleapis.com/auth/calendar.readonly',  # 只读权限
    # 'https://www.googleapis.com/auth/calendar.events',  # 事件访问权限
    # 'https://www.googleapis.com/auth/calendar.events.readonly',  # 事件只读权限
    # 'https://www.googleapis.com/auth/calendar.settings',  # 设置访问权限
    # 'https://www.googleapis.com/auth/calendar.settings.readonly',  # 设置只读权限
]

# 认证配置
# CLIENT_SECRET_FILE = 'client_secret_947248835406-osf26cbrtboo53rpstn0grso36oa76he.apps.googleusercontent.com.json'  # OAuth 客户端密钥文件
CLIENT_SECRET_FILE = 'desktop_client_secret_947248835406-6kbi4f28vm6n25gpuqrhpo5ltjp1vqid.apps.googleusercontent.com.json'  # OAuth 客户端密钥文件
CREDENTIALS_FILE = 'token.json'  # 存储的凭据文件

# 默认日历ID
PRIMARY_CALENDAR_ID = 'primary'  # 'primary' 表示用户的主日历

# 时间设置
TIMEZONE = 'Asia/Shanghai'  # 默认时区
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'  # 日期时间格式
DATE_FORMAT = '%Y-%m-%d'  # 日期格式

# API调用配置
MAX_RESULTS = 100  # 每次查询的最大结果数
QUOTA_LIMIT = 10000  # 每日配额限制

# 颜色映射
COLOR_MAP = {
    '1': '#7986CB',  # 蓝色
    '2': '#33B679',  # 青绿色
    '3': '#8E24AA',  # 紫色
    '4': '#E67C73',  # 红色
    '5': '#F4511E',  # 橙色
    '6': '#3F51B5',  # 深蓝色
    '7': '#0B8043',  # 深绿色
    '8': '#C2185B',  # 玫红色
    '9': '#3F51B5',  # 深蓝色
    '10': '#7986CB',  # 浅蓝色
    '11': '#33B679',  # 浅青绿色
}

# 事件类型
EVENT_TYPES = {
    'default': '常规事件',
    'birthday': '生日事件（年度重复的全天事件）',
    'focusTime': '专注时间事件',
    'outOfOffice': '外出事件',
    'workingLocation': '工作地点事件',
    'fromGmail': '来自Gmail的事件（无法创建）',
}

# 访问角色
ACCESS_ROLES = {
    'freeBusyReader': '仅查看忙闲信息',
    'reader': '查看日历（隐藏私人事件详情）',
    'writer': '读写日历权限',
    'owner': '管理权限（可修改其他用户权限）',
}

# 事件状态
EVENT_STATUS = {
    'confirmed': '已确认',
    'tentative': '待确认',
    'cancelled': '已取消',
}

# 提醒方式
REMINDER_METHODS = {
    'email': '邮件提醒',
    'popup': '弹窗提醒',
}

# 日历日期格式
ICAL_DATETIME_FORMAT = '%Y%m%dT%H%M%SZ'
ICAL_DATE_FORMAT = '%Y%m%d'
