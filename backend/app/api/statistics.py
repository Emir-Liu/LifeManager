"""
统计分析 API
"""
from fastapi import APIRouter

router = APIRouter()

# TODO: 实现统计相关接口


@router.get("/overview")
async def get_statistics_overview():
    """获取统计概览"""
    return {"message": "统计分析接口开发中", "code": 200}
