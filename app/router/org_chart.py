from fastapi import APIRouter, Query, Path, HTTPException
from app.db.org_chart import db_get_organizational_chart

router = APIRouter()

@router.get('/org_chart/full', tags=['org_chart'])
async def get_organizational_chart(
    dept_no: str | None = Query(None, description="Department number (e.g., 'd005'), returns all departments if not specified"),
    limit: int = Query(100, ge=1, le=100, description="Limit of returned records, default is 100")
):
    """
    Retrieve organizational chart (using recursive CTE)
    
    **True recursive implementation**:
    - Level 1: Current department managers (manager_emp_no = NULL)
    - Level 2: Department employees (manager_emp_no = manager's emp_no)
    
    Returned results include the manager_emp_no field to show reporting relationships.
    
    **Note**: Only includes current managers (to_date = '9999-01-01')
    """
    try:
        result = db_get_organizational_chart(dept_no=dept_no, limit=limit)
        
        if not result:
            raise HTTPException(status_code=404, detail="No organizational chart data found")
        
        # Summary statistics
        managers = [r for r in result if r['level'] == 1]
        employees = [r for r in result if r['level'] == 2]
        
        return {
            "total_records": len(result),
            "managers_count": len(managers),
            "employees_count": len(employees),
            "dept_no_filter": dept_no,
            "note": "The manager_emp_no field indicates each employee's direct supervisor (current manager)",
            "hierarchy": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
