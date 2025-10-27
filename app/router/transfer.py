from fastapi import APIRouter, Query
from app.db.transfer import db_get_transfers

router = APIRouter()


@router.get('/transfer/list', tags=['transfer'])
async def get_transfers(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    start_date: str | None = Query(None, description="开始日期，格式 YYYY-MM-DD，默认 90 天前"),
    end_date: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD，默认今天"),
):
    """
    获取部门间调动记录，用于分析内部流动模式。
    """
    return db_get_transfers(pageNo=page, pageSize=10,start_date=start_date, end_date=end_date)
