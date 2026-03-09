"""
Redis 配置
"""
import redis
from app.core.config import settings

# 创建 Redis 连接
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    health_check_interval=30
)


async def redis_health_check() -> bool:
    """检查 Redis 连接是否正常"""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
