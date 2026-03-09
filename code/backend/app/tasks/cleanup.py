"""
清理相关任务
"""
from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.cleanup.cleanup_expired_reminders")
def cleanup_expired_reminders():
    """
    清理过期的提醒记录

    每天执行一次
    """
    logger.info("开始清理过期提醒...")

    # TODO: 实现清理逻辑
    # 1. 删除30天前的已发送提醒
    # 2. 清理无效的统计缓存

    logger.info("过期提醒清理完成")

    return {"status": "success", "cleaned_count": 0}
