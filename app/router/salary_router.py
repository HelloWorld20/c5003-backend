from fastapi import APIRouter, Query
# from sqlalchemy import text, create_engine
from app.db.salary_db import db_salary_list, db_add_salary, db_update_salary, db_del_salary

router = APIRouter()

@router.get('/salary/list', tags=['Salaries'])
async def get_salary_list(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
    Employee_ID: int | None = Query(None, description="Optional"),
    Salary: int | None = Query(None, description="Optional"),
    From_Date: str | None = Query(None, description="Optional"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Obtain salary information and feed to the frontend.
    """
    return db_salary_list(**locals())

@router.post('/salary/addition', tags=['Salaries'])
async def add_salary(
    Employee_ID: int = Query(..., description="Mandatory"),
    Salary: int = Query(..., description="Mandatory"),
    From_Date: str = Query(..., description="Mandatory"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Add salary records.
    """
    effective_to_date = '9999-01-01' if To_Date is None else To_Date
    return db_add_salary(Employee_ID=Employee_ID, Salary=Salary, From_Date=From_Date, To_Date = effective_to_date)

@router.put('/salary/update', tags=['Salaries'])
async def update_dept_emp(
    Employee_ID: int = Query(..., description="Mandatory"),
    Salary: int = Query(..., description="Mandatory"),
    From_Date: str = Query(..., description="Mandatory"),
    To_Date: str = Query(..., description="Mandatory"),
):
    """
    Update employee salary end_date.
    """
    return db_update_salary(Employee_ID=Employee_ID, Salary=Salary, From_Date=From_Date, To_Date=To_Date)

@router.delete('/salary/deletion', tags=['Salaries'])
async def delete_salary(Employee_ID: int, Salary: int):
    """
    Delete department employee.
    """
    return db_del_salary(Employee_ID=Employee_ID, Salary=Salary)