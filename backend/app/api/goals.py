"""
目标管理 API
"""
from fastapi import APIRouter

router = APIRouter()

# TODO: 实现目标相关接口


@router.get("/")
async def get_goals():
    """获取目标列表"""
    return {"message": "目标管理接口开发中", "code": 200}


@router.post("/")
async def create_goal():
    """创建目标"""
    return {"message": "创建目标接口开发中", "code": 200}
