from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.dept_manager_db import db_dept_manager_list, db_dept_manager_list_all, db_add_dept_manager, db_update_dept_manager, db_del_dept_manager

router = APIRouter()

class DeptManagerCreate(BaseModel):
    """
    Department manager creation request body model
    - Field alias compatibility: `emp_no/dept_no/from_date/to_date` and `Employee_ID/Dept_Number/From_Date/To_Date`
    - `to_date` is optional, defaults to `'9999-01-01'`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptManagerUpdate(BaseModel):
    """
    Department manager update request body model
    - All fields are required to uniquely identify the record
    - Commonly used to update `to_date`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str = Field(..., validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptManagerDelete(BaseModel):
    """
    Department manager deletion request body model
    - Compatible with two field naming styles: `emp_no/dept_no` and `Employee_ID/Dept_Number`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))

@router.get('/dept_manager/list', tags=['Department Managers'])
async def get_dept_manager_list(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
    Employee_ID: int | None = Query(None, description="Optional"),
    Dept_Number: str | None = Query(None, description="Optional"),
    From_Date: str | None = Query(None, description="Optional"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Obtain current department manager information (only managers with MAX(to_date) = '9999-01-01').
    """
    return db_dept_manager_list(**locals())

@router.get('/dept_manager/list/all', tags=['Department Managers'])
async def get_dept_manager_list_all(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
    Employee_ID: int | None = Query(None, description="Optional"),
    Dept_Number: str | None = Query(None, description="Optional"),
    From_Date: str | None = Query(None, description="Optional"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Obtain all department manager information (including historical records).
    """
    return db_dept_manager_list_all(**locals())

@router.post('/dept_manager/addition', tags=['Department Managers'])
async def add_dept_manager(payload: DeptManagerCreate = Body(..., description="Department manager creation information, pass as JSON")):
    """
    Create a new department manager record.
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_dept_manager(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/dept_manager/update', tags=['Department Managers'])
async def update_dept_manager(payload: DeptManagerUpdate = Body(..., description="Department manager update information, pass as JSON")):
    """
    Update department manager's department assignment and date range (commonly used to update `to_date`).
    """
    return db_update_dept_manager(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=payload.to_date)

@router.delete('/dept_manager/deletion', tags=['Department Managers'])
async def delete_dept_manager(payload: DeptManagerDelete = Body(..., description="Department manager deletion information, pass as JSON")):
    """
    Delete department manager record.
    """
    return db_del_dept_manager(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no)