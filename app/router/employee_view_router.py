# In app/router/employee_view_router.py

from fastapi import APIRouter, Query
from typing import Optional
from app.db.employee_view_db import employee_profile

router = APIRouter()

@router.get('/employees/view', tags=['Employees'])
async def get_employees_view(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
    Employee_ID_min: Optional[int] = Query(None, description="Optional"),
    Employee_ID_max: Optional[int] = Query(None, description="Optional"),
    Employee_Name: Optional[str] = Query(None, description="Optional"),
    Title: Optional[str] = Query(None, description="Optional"),
    Salary_min: Optional[int] = Query(None, description="Optional"),
    Salary_max: Optional[int] = Query(None, description="Optional"),
    Department_Number: Optional[str] = Query(None, description="Optional"),
    Department: Optional[str] = Query(None, description="Optional"),
    Manager_Name: Optional[str] = Query(None, description="Optional"),
    Effective_Date_min: Optional[str] = Query(None, description="Optional"),
    Effective_Date_max: Optional[str] = Query(None, description="Optional"),
    End_Date_min: Optional[str] = Query(None, description="Optional"),
    End_Date_max: Optional[str] = Query(None, description="Optional"),
):
    """
    Obtain employee history/profile information and feed to the frontend.
    """
    # Pass all parameters to employee_profile function
    params = {
        'Page_Number': Page_Number,
        'Row_Count': Row_Count,
        'Employee_ID_min': Employee_ID_min,
        'Employee_ID_max': Employee_ID_max,
        'Employee_Name': Employee_Name,
        'Title': Title,
        'Salary_min': Salary_min,
        'Salary_max': Salary_max,
        'Department_Number': Department_Number,
        'Department': Department,
        'Manager_Name': Manager_Name,
        'Effective_Date_min': Effective_Date_min,
        'Effective_Date_max': Effective_Date_max,
        'End_Date_min': End_Date_min,
        'End_Date_max': End_Date_max
    }
    return employee_profile(**params)
