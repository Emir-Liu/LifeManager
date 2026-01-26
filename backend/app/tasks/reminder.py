"""
提醒相关任务
"""
from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.reminder.check_reminders")
def check_reminders():
    """
    检查并发送提醒

    每分钟执行一次
    """
    logger.info("开始检查待发送的提醒...")

    # TODO: 实现提醒检查逻辑
    # 1. 从数据库查询即将到期的提醒
    # 2. 通过 FCM 发送推送通知
    # 3. 更新提醒状态

    logger.info("提醒检查完成")

    return {"status": "success", "checked_count": 0}
