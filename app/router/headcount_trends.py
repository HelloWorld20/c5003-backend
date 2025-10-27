from fastapi import APIRouter, Query, HTTPException
from app.db.headcount_trends import db_get_headcount_changes_by_year



router = APIRouter()



@router.get('/headcount/changes', tags=['headcount'])
async def get_headcount_changes(
    start_year: int | None = Query(None, ge=1985, le=2025, description="Start year"),
    end_year: int | None = Query(None, ge=1985, le=2025, description="End year")
):
    """
    Get comprehensive headcount changes by year
    
    Returns for each year:
    - Number of new hires
    - Number of departures
    - Net change (hires - departures)
    - Turnover rate percentage
    
    **This is the core interface for monitoring hiring trends and employee turnover**
    """
    result = db_get_headcount_changes_by_year(start_year, end_year)
    
    if not result:
        raise HTTPException(status_code=404, detail="Headcount change data not found")
    
    total_hires = sum(row["new_hires"] for row in result)
    total_departures = sum(row["departures"] for row in result)
    
    return {
        "start_year": start_year or result[0]["year"],
        "end_year": end_year or result[-1]["year"],
        "total_years": len(result),
        "summary": {
            "total_hires": total_hires,
            "total_departures": total_departures,
            "net_change": total_hires - total_departures,
            "overall_turnover_rate_percent": round(total_departures * 100.0 / total_hires, 2) if total_hires > 0 else 0
        },
        "data": result
    }
