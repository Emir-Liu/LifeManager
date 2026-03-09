"""
统计相关任务
"""
from celery import shared_task
from loguru import logger


@shared_task(name="app.tasks.statistics.update_statistics")
def update_statistics():
    """
    更新统计数据

    每天执行一次
    """
    logger.info("开始更新统计数据...")

    # TODO: 实现统计更新逻辑
    # 1. 计算用户的任务完成率
    # 2. 计算目标进度
    # 3. 更新缓存

    logger.info("统计数据更新完成")

    return {"status": "success"}
