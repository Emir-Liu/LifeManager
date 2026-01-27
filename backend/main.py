"""
LifeManager 主应用入口
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, goals, plans, tasks, reminders, statistics


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="托管人生 - 智能目标管理应用 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 (注意: auth 没有前缀,其他 router 有前缀)
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api", tags=["用户"])
app.include_router(goals.router, prefix="/api", tags=["目标"])
app.include_router(plans.router, prefix="/api", tags=["规划"])
app.include_router(tasks.router, prefix="/api", tags=["任务"])
app.include_router(reminders.router, prefix="/api", tags=["提醒"])
app.include_router(statistics.router, prefix="/api", tags=["统计"])


# @app.get("/")
# async def root():
#     """根路径"""
#     return {
#         "app": settings.APP_NAME,
#         "version": settings.APP_VERSION,
#         "status": "running",
#         "docs": "/docs"
#     }


# @app.get("/health")
# async def health_check():
#     """健康检查"""
#     return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
