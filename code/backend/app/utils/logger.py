"""
日志工具模块
提供统一的日志记录功能
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import settings


class Logger:
    """日志管理器"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str = "LifeManager") -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            Logger实例
        """
        if name in cls._loggers:
            return cls._loggers[name]

        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

        # 避免重复添加handler
        if logger.handlers:
            return logger

        # 创建格式化器
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            log_dir / f"{name.lower()}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 缓存日志记录器
        cls._loggers[name] = logger

        return logger

    @classmethod
    def clear_handlers(cls, name: str):
        """清除指定日志记录器的所有handler"""
        if name in cls._loggers:
            logger = cls._loggers[name]
            logger.handlers.clear()


# 创建默认日志记录器
logger = Logger.get_logger("LifeManager")
