from fastapi import APIRouter, Query
from app.db.long_single_role import db_get_long_single_role

router = APIRouter()


@router.get('/long_single_role/candidates', tags=['long_single_role'])
async def get_long_single_role_candidates(
    min_days: int = Query(1095, ge=1, description="在同一职位的最短天数阈值，默认 1095（约 3 年）"),
    as_of_date: str | None = Query(None, description="计算截止日期，格式 YYYY-MM-DD，默认今天"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数上限，默认 100"),
):
    """
    获取在同一职位长期停留的员工候选列表，便于培训或晋升评估。
    """
    return db_get_long_single_role(min_days=min_days, as_of_date=as_of_date, limit=limit)
