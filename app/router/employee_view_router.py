# In app/router/employee_view_router.py

from fastapi import APIRouter, Query
from app.db.employee_view_db import employee_profile

router = APIRouter()

@router.get('/employees/view', tags=['Employees View'])
async def get_employees_view(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
    Employee_ID: int | None = Query(None, description="Optional"),
    Employee_Name: str | None = Query(None, description="Optional"),
    Title: str | None = Query(None, description="Optional"),
    Salary: int | None = Query(None, description="Optional"),
    Department_Number: str | None = Query(None, description="Optional"),
    Department: str | None = Query(None, description="Optional"),
    Manager_Name: str | None = Query(None, description="Optional"),
    Effective_Date: str | None = Query(None, description="Optional"),
    End_Date: str | None = Query(None, description="Optional"),
):
    """
    Obtain employee general information and feed to the frontend.
    """
    return employee_profile(**locals())
