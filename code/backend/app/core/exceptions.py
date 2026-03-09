"""
错误码定义
"""


class ErrorCode:
    """错误码常量"""

    # 通用错误
    SUCCESS = 0
    COMMON_ERROR = 1

    # 认证错误 (1001-1099)
    USERNAME_EXISTS = 1001
    PARAM_ERROR = 1002
    USER_NOT_FOUND = 1003
    PASSWORD_ERROR = 1004
    TOKEN_INVALID = 1005
    TOKEN_EXPIRED = 1006

    # 目标错误 (2001-2099)
    GOAL_NOT_FOUND = 2001
    GOAL_NOT_BELONG_TO_USER = 2002
    GOAL_TITLE_EMPTY = 2003

    # 规划错误 (3001-3099)
    PLAN_NOT_FOUND = 3001
    PLAN_CONFIRMED_CANNOT_MODIFY = 3002
    PLAN_GENERATE_FAILED = 3003

    # 任务错误 (4001-4099)
    TASK_NOT_FOUND = 4001
    TASK_NOT_BELONG_TO_USER = 4002

    # AI 错误 (5001-5099)
    AI_SERVICE_UNAVAILABLE = 5001
    AI_GENERATE_FAILED = 5002


# 错误消息映射
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "成功",
    ErrorCode.COMMON_ERROR: "通用错误",

    # 认证错误
    ErrorCode.USERNAME_EXISTS: "用户名已存在",
    ErrorCode.PARAM_ERROR: "参数错误",
    ErrorCode.USER_NOT_FOUND: "用户不存在",
    ErrorCode.PASSWORD_ERROR: "密码错误",
    ErrorCode.TOKEN_INVALID: "Token无效",
    ErrorCode.TOKEN_EXPIRED: "Token已过期",

    # 目标错误
    ErrorCode.GOAL_NOT_FOUND: "目标不存在",
    ErrorCode.GOAL_NOT_BELONG_TO_USER: "目标不属于当前用户",
    ErrorCode.GOAL_TITLE_EMPTY: "目标标题不能为空",

    # 规划错误
    ErrorCode.PLAN_NOT_FOUND: "规划不存在",
    ErrorCode.PLAN_CONFIRMED_CANNOT_MODIFY: "规划已确认，无法修改",
    ErrorCode.PLAN_GENERATE_FAILED: "规划生成失败",

    # 任务错误
    ErrorCode.TASK_NOT_FOUND: "任务不存在",
    ErrorCode.TASK_NOT_BELONG_TO_USER: "任务不属于当前用户",

    # AI 错误
    ErrorCode.AI_SERVICE_UNAVAILABLE: "AI服务不可用",
    ErrorCode.AI_GENERATE_FAILED: "AI生成失败",
}
