"""
任务管理 API
"""
from fastapi import APIRouter

router = APIRouter()

# TODO: 实现任务相关接口


@router.get("/today")
async def get_today_tasks():
    """获取今日任务"""
    return {"message": "今日任务接口开发中", "code": 200}


@router.get("/")
async def get_tasks():
    """获取任务列表"""
    return {"message": "任务管理接口开发中", "code": 200}
