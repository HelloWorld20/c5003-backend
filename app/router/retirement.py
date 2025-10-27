from fastapi import APIRouter, Query, HTTPException
from app.db.retirement import db_get_retirement_candidates

router = APIRouter()

@router.get('/retirement/age', tags=['retirement'])
async def get_retirement_candidates(
    retirement_age: int = Query(65, ge=60, le=70, description="Retirement age threshold. Use 60 for early retirement, 65 for normal retirement"),
    dept_no: str | None = Query(None, description="Department number (e.g., 'd005'), returns all departments if not specified"),
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page, default is 10, max is 100")
):
    """
    Retrieve a list of employees nearing retirement (based on birth year ≤ current year - retirement age).
    
    **Pagination Support:**
    - page: Page number (starting from 1)
    - page_size: Records per page (default 100, max 500)
    
    **Example:**
    - Page 1: GET /retirement/age?page=1&page_size=100 (records 1-100)
    - Page 2: GET /retirement/age?page=2&page_size=100 (records 101-200)
    - Page 3: GET /retirement/age?page=3&page_size=100 (records 201-300)
    
    Note: 60 years is considered early retirement, 65 years is normal retirement.
    """

    try:
        result = db_get_retirement_candidates(
            dept_no=dept_no, 
            retirement_age=retirement_age, 
            limit=page_size,
            page=page
        )
        
        if not result or not result.get("data"):
            raise HTTPException(status_code=404, detail="No retirement candidates found")
        
        return {
            "retirement_age": retirement_age,
            "dept_no_filter": dept_no,
            "pagination": {
                "current_page": result["page"],
                "page_size": result["page_size"],
                "total_pages": result["total_pages"],
                "total_records": result["total_count"]
            },
            "retirement_candidates": result["data"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")