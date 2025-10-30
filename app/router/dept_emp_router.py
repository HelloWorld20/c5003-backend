from fastapi import APIRouter, Query
# from sqlalchemy import text, create_engine
from app.db.dept_emp_db import db_dept_emp_list, db_add_dept_emp, db_update_dept_emp, db_del_dept_emp

router = APIRouter()

@router.get('/dept_emp/list', tags=['Department Employees'])
async def get_dept_emp_list(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
    Employee_ID: int | None = Query(None, description="Optional"),
    Dept_Number: str | None = Query(None, description="Optional"),
    From_Date: str | None = Query(None, description="Optional"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Obtain department employee information and feed to the frontend.
    """
    return db_dept_emp_list(**locals())

@router.post('/dept_emp/addition', tags=['Department Employees'])
async def add_dept_emp(
    Employee_ID: int = Query(..., description="Mandatory"),
    Dept_Number: str = Query(..., description="Mandatory"),
    From_Date: str = Query(..., description="Mandatory"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Add department employee.
    """
    effective_to_date = '9999-01-01' if To_Date is None else To_Date
    return db_add_dept_emp(Employee_ID=Employee_ID, Dept_Number=Dept_Number, From_Date=From_Date, To_Date = effective_to_date)

@router.put('/dept_emp/update', tags=['Department Employees'])
async def update_dept_emp(
    Employee_ID: int = Query(..., description="Mandatory"),
    Dept_Number: str = Query(..., description="Mandatory"),
    From_Date: str = Query(..., description="Mandatory"),
    To_Date: str = Query(..., description="Mandatory"),
):
    """
    Update employee department, start_date and end_date.
    """
    return db_update_dept_emp(Employee_ID=Employee_ID, Dept_Number=Dept_Number, From_Date=From_Date, To_Date=To_Date)

@router.delete('/dept_emp/deletion', tags=['Department Employees'])
async def delete_dept_emp(Employee_ID: int, Dept_Number: str):
    """
    Delete department employee.
    """
    return db_del_dept_emp(Employee_ID=Employee_ID, Dept_Number=Dept_Number)