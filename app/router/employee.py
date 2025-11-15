from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
from typing import Optional
# from sqlalchemy import text, create_engine
from app.db.employee import db_get_emp_list, db_add_emp, db_del_emp, db_update_emp, get_emp_info

router = APIRouter()


class EmployeeUpdate(BaseModel):
    """
    Employee update request body model
    - Optional fields: `birth_date`, `hire_date`, `gender`, `name`, `first_name`, `last_name`, `emp_no`
    - Supports passing either `name` or `first_name` + `last_name`, router layer will merge them
    """
    emp_no: Optional[int] = None
    birth_date: Optional[str] = None
    hire_date: Optional[str] = None
    gender: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dept_no: Optional[str] = None
    title: Optional[str] = None
    salary: Optional[int] = None


class EmployeeCreate(BaseModel):
    """
    Employee creation request body model
    - Required fields: `birth_date`, `hire_date`, `gender`
    - Optional fields: `name` or `first_name` + `last_name`
    - If both `name` and `first_name/last_name` are provided, `name` takes priority
    """
    birth_date: str
    hire_date: str
    gender: str
    emp_no: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dept_no: Optional[str] = None
    salary: Optional[int] = None
    title: Optional[str] = None



@router.get('/employees/list', tags=['Employees'])
async def get_employees_list(
    page: int = Query(..., description="Mandatory"),
    pageSize: int = Query(..., description="Mandatory"),
    emp_no_min: Optional[int] = Query(None, description="Optional"),
    emp_no_max: Optional[int] = Query(None, description="Optional"),
    birth_date_min: Optional[str] = Query(None, description="Optional"),
    birth_date_max: Optional[str] = Query(None, description="Optional"),
    hire_date_min: Optional[str] = Query(None, description="Optional"),
    hire_date_max: Optional[str] = Query(None, description="Optional"),
    name: Optional[str] = Query(None, description="Optional"),
    gender: Optional[str] = Query(None, description="Optional"),
    salary_min: Optional[int] = Query(None, description="Optional"),
    salary_max: Optional[int] = Query(None, description="Optional"),
    dept_name: Optional[str] = Query(None, description="Optional"),
    title: Optional[str] = Query(None, description="Optional"),
):
    """
    Obtain employee information and feed to the frontend.
    """
    return db_get_emp_list(**locals())

@router.post('/employees', tags=['Employees'])
async def add_employee(payload: EmployeeCreate = Body(..., description="Employee creation information, pass as JSON")):
    """
    Create a new employee record.
    """
    # Normalize name: prioritize name; otherwise concatenate first_name + last_name
    resolved_name = payload.name
    if not resolved_name and (payload.first_name or payload.last_name):
        first = payload.first_name or ""
        last = payload.last_name or ""
        resolved_name = (first + (" " + last if last else "")) or ""

    return db_add_emp(
        emp_no=payload.emp_no,
        gender=payload.gender,
        birth_date=payload.birth_date,
        hire_date=payload.hire_date,
        name=resolved_name,
        dept_no=payload.dept_no,
        salary=payload.salary,
        title=payload.title,
    )

@router.put('/employees/{emp_no}', tags=['Employees'])
async def update_employee(
    emp_no: int,
    payload: EmployeeUpdate = Body(..., description="Employee update information, pass as JSON")
):
    """
    Update employee information by employee number.
    """
    # Normalize name to "first + space + last" format; keep as None if not provided
    resolved_name = payload.name
    if not resolved_name and (payload.first_name or payload.last_name):
        first = payload.first_name or ""
        last = payload.last_name or ""
        resolved_name = (first + (" " + last if last else "")) or None

    return db_update_emp(
        emp_no=emp_no,
        gender=payload.gender,
        birth_date=payload.birth_date,
        hire_date=payload.hire_date,
        name=resolved_name,
        dept_no=payload.dept_no,
        title=payload.title,
        salary=payload.salary,
    )

@router.delete('/employees/{emp_no}', tags=['Employees'])
async def delete_employee(emp_no: int):
    """
    Delete employee record by employee number.
    """
    return db_del_emp(emp_no=emp_no)

@router.get('/employees/{emp_no}', tags=['Employees'])
async def get_employee_info(emp_no: int):
    """
    Obtain employee information by employee number.
    """
    return get_emp_info(emp_no=emp_no)