from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.salary_db import db_salary_list, db_add_salary, db_update_salary, db_del_salary

router = APIRouter()

class SalaryCreate(BaseModel):
    """
    Salary creation request body model
    - Compatible with two field naming styles:
      - Frontend common: `emp_no`, `salary`, `from_date`, `to_date`
      - Legacy API style: `Employee_ID`, `Salary`, `From_Date`, `To_Date`
    - `to_date` is optional, defaults to `'9999-01-01'` at router layer
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    salary: int = Field(..., validation_alias=AliasChoices('salary', 'Salary'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class SalaryUpdate(BaseModel):
    """
    Salary update request body model
    - Used to update the end date of a salary record
    - All fields are required to uniquely identify the record
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    salary: int = Field(..., validation_alias=AliasChoices('salary', 'Salary'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str = Field(..., validation_alias=AliasChoices('to_date', 'To_Date'))

class SalaryDelete(BaseModel):
    """
    Salary deletion request body model
    - Compatible with two field naming styles: `emp_no/salary` and `Employee_ID/Salary`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    salary: int = Field(..., validation_alias=AliasChoices('salary', 'Salary'))

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
async def add_salary(payload: SalaryCreate = Body(..., description="Salary creation information, pass as JSON")):
    """
    Create a new salary record.
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_salary(Employee_ID=payload.emp_no, Salary=payload.salary, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/salary/update', tags=['Salaries'])
async def update_dept_emp(payload: SalaryUpdate = Body(..., description="Salary update information, pass as JSON")):
    """
    Update employee salary record end date.
    """
    return db_update_salary(Employee_ID=payload.emp_no, Salary=payload.salary, From_Date=payload.from_date, To_Date=payload.to_date)

@router.delete('/salary/deletion', tags=['Salaries'])
async def delete_salary(payload: SalaryDelete = Body(..., description="Salary deletion information, pass as JSON")):
    """
    Delete employee salary record.
    """
    return db_del_salary(Employee_ID=payload.emp_no, Salary=payload.salary)