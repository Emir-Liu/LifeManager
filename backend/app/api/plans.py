"""
规划管理 API
"""
from fastapi import APIRouter

router = APIRouter()

# TODO: 实现规划相关接口


@router.get("/")
async def get_plans():
    """获取规划列表"""
    return {"message": "规划管理接口开发中", "code": 200}


@router.post("/generate")
async def generate_plan():
    """生成规划"""
    return {"message": "生成规划接口开发中", "code": 200}
