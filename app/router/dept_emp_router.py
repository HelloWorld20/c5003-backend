from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.dept_emp_db import db_dept_emp_list, db_add_dept_emp, db_update_dept_emp, db_del_dept_emp

router = APIRouter()

class DeptEmpCreate(BaseModel):
    """
    Department employee creation request body model
    - Field alias compatibility: `emp_no/dept_no/from_date/to_date` and `Employee_ID/Dept_Number/From_Date/To_Date`
    - `to_date` is optional, defaults to `'9999-01-01'`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptEmpUpdate(BaseModel):
    """
    Department employee update request body model
    - Updates the end date of a specific record (can also be used to adjust department/date range)
    - All fields are required to uniquely identify the record
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str = Field(..., validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptEmpDelete(BaseModel):
    """
    Department employee deletion request body model
    - Compatible with two field naming styles: `emp_no/dept_no` and `Employee_ID/Dept_Number`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))

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
async def add_dept_emp(payload: DeptEmpCreate = Body(..., description="Department employee creation information, pass as JSON")):
    """
    Create a new department employee record.
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_dept_emp(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/dept_emp/update', tags=['Department Employees'])
async def update_dept_emp(payload: DeptEmpUpdate = Body(..., description="Department employee update information, pass as JSON")):
    """
    Update employee's department assignment and date range (commonly used to update `to_date`).
    """
    return db_update_dept_emp(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=payload.to_date)

@router.delete('/dept_emp/deletion', tags=['Department Employees'])
async def delete_dept_emp(payload: DeptEmpDelete = Body(..., description="Department employee deletion information, pass as JSON")):
    """
    Delete department employee record.
    """
    return db_del_dept_emp(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no)