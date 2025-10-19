from fastapi import APIRouter, Query
from app.db.promotion import db_get_internal_mobility, db_get_recent_promotions

router = APIRouter()


@router.get('/promotion/internal_mobility', tags=['promotion'])
async def get_internal_mobility(
    start_date: str | None = Query(None, description="开始日期，格式 YYYY-MM-DD，默认 90 天前"),
    end_date: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD，默认今天"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数上限，默认 100"),
):
    """
    查询指定时间段内发生部门变动的员工（内部流动）。
    """
    return db_get_internal_mobility(start_date=start_date, end_date=end_date, limit=limit)


@router.get('/promotion/recent', tags=['promotion'])
async def get_recent_promotions(
    window_days: int = Query(90, ge=1, description="向前查询的天数窗口，默认 90 天"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数上限，默认 100"),
):
    """
    查询最近一段时间内发生职称变化（视为晋升）的员工。
    """
    return db_get_recent_promotions(window_days=window_days, limit=limit)
