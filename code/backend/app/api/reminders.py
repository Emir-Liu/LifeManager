"""
提醒管理 API
"""
from fastapi import APIRouter

router = APIRouter()

# TODO: 实现提醒相关接口


@router.get("/")
async def get_reminders():
    """获取提醒列表"""
    return {"message": "提醒管理接口开发中", "code": 200}
