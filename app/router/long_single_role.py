from fastapi import APIRouter, Query
from app.db.long_single_role import db_get_long_single_role

router = APIRouter()


@router.get('/long_single_role/candidates', tags=['long_single_role'])
async def get_long_single_role_candidates(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    min_days: int = Query(1095, ge=1, description="在同一职位的最短天数阈值，默认 1095（约 3 年）"),
    as_of_date: str | None = Query(None, description="计算截止日期，格式 YYYY-MM-DD，默认今天"),
):
    """
    获取在同一职位长期停留的员工候选列表（分页，每页10条，最多100条）。
    """
    # 每页固定 10 条，数据库层会强制总数上限为 100
    return db_get_long_single_role(pageNo=page, pageSize=10, min_days=min_days, as_of_date=as_of_date)

