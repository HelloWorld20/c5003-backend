from fastapi import APIRouter, Query, HTTPException
from app.db.retirement import db_get_retirement_candidates

router = APIRouter()

@router.get('/retirement/age', tags=['retirement'])
async def get_retirement_candidates(
    retirement_age: int = Query(65, ge=60, le=65, description="Retirement age threshold. Use 60 for early retirement, 65 for normal retirement"),
    dept_no: str | None = Query(None, description="Department number (e.g., 'd005'), returns all departments if not specified"),
    limit: int = Query(100, ge=1, le=100, description="Limit of returned records, default is 100")
):

    """
    Retrieve a list of employees nearing retirement (based on birth year ≤ current year - retirement age).
    Note: 60 years is considered early retirement, 65 years is normal retirement.
    """

    try:
        result = db_get_retirement_candidates(dept_no=dept_no, retirement_age=retirement_age, limit=limit)
        if not result:
            raise HTTPException(status_code=404, detail="No retirement candidates found")
        return {
            "total_candidates": len(result),
            "retirement_age": retirement_age,
            "dept_no_filter": dept_no,
            "retirement_candidates": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")