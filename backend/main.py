"""
LifeManager 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, goals, plans, tasks, reminders, statistics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    logger.info(f"Debug 模式: {settings.DEBUG}")
    logger.info(f"数据库: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")

    # 创建数据库表
    Base.metadata.create_all(bind=engine)

    yield

    # 关闭时执行
    logger.info(f"{settings.APP_NAME} 正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="托管人生 - 智能目标管理应用 API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/v1/users", tags=["用户"])
app.include_router(goals.router, prefix="/v1/goals", tags=["目标"])
app.include_router(plans.router, prefix="/v1/plans", tags=["规划"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["任务"])
app.include_router(reminders.router, prefix="/v1/reminders", tags=["提醒"])
app.include_router(statistics.router, prefix="/v1/statistics", tags=["统计"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
