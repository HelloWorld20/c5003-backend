from fastapi import APIRouter, Query
from app.db.transfer import db_get_transfers

router = APIRouter()


@router.get('/transfer/list', tags=['transfer'])
async def get_transfers(
    start_date: str | None = Query(None, description="开始日期，格式 YYYY-MM-DD，默认 90 天前"),
    end_date: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD，默认今天"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数上限，默认 100"),
):
    """
    获取部门间调动记录，用于分析内部流动模式。
    """
    return db_get_transfers(start_date=start_date, end_date=end_date, limit=limit)
