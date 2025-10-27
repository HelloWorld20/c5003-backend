from fastapi import APIRouter, Query, Path, HTTPException
from app.db.org_chart import db_get_organizational_chart

router = APIRouter()


@router.get('/org_chart/full', tags=['org_chart'])
async def get_organizational_chart(
    dept_no: str | None = Query(None, description="Department number (e.g., 'd005'), returns all departments if not specified"),
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page, default is 10, max is 100")
):
    """
    Retrieve organizational chart (using recursive CTE with pagination)
    
    **True recursive implementation**:
    - Level 1: Current department managers (manager_emp_no = NULL)
    - Level 2: Department employees (manager_emp_no = manager's emp_no)
    
    **Pagination Support:**
    - page: Page number (starting from 1)
    - page_size: Records per page (default 100, max 500)
    
    **Example:**
    - Page 1: GET /org_chart/full?page=1&page_size=100 (records 1-100)
    - Page 2: GET /org_chart/full?page=2&page_size=100 (records 101-200)
    - Page 3: GET /org_chart/full?page=3&page_size=100 (records 201-300)
    
    Returned results include the manager_emp_no field to show reporting relationships.
    
    **Note**: Only includes current managers (to_date = '9999-01-01')
    """
    try:
        result = db_get_organizational_chart(dept_no=dept_no, limit=page_size, page=page)
        
        if not result or not result.get("data"):
            raise HTTPException(status_code=404, detail="No organizational chart data found")
        
        # Summary statistics (only for current page)
        managers = [r for r in result["data"] if r['level'] == 1]
        employees = [r for r in result["data"] if r['level'] == 2]
        
        return {
            "dept_no_filter": dept_no,
            "pagination": {
                "current_page": result["page"],
                "page_size": result["page_size"],
                "total_pages": result["total_pages"],
                "total_records": result["total_count"]
            },
            "current_page_summary": {
                "records_on_page": len(result["data"]),
                "managers_on_page": len(managers),
                "employees_on_page": len(employees)
            },
            "note": "The manager_emp_no field indicates each employee's direct supervisor (current manager)",
            "hierarchy": result["data"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")