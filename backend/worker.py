"""
Celery Worker 配置
"""
from celery import Celery
from app.core.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "lifemanager",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.reminder",
        "app.tasks.statistics",
        "app.tasks.cleanup"
    ]
)

# 配置 Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    worker_prefetch_multiplier=1,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    'check-reminders-every-minute': {
        'task': 'app.tasks.reminder.check_reminders',
        'schedule': 60.0,  # 每分钟检查一次
    },
    'cleanup-expired-reminders-daily': {
        'task': 'app.tasks.cleanup.cleanup_expired_reminders',
        'schedule': 86400.0,  # 每天清理一次
    },
}


if __name__ == "__main__":
    celery_app.start()
