from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.dept_db import db_dept_list, db_add_dept, db_update_dept, db_del_dept, db_get_dept_info

router = APIRouter()

class DepartmentCreate(BaseModel):
    """
    Department creation request body model
    - Supports field alias compatibility: `dept_no`/`Dept_ID` and `dept_name`/`Dept_Name`
    - Purpose: Prevents 422 validation errors when frontend uses different naming styles
    """
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_ID'))
    dept_name: str = Field(..., validation_alias=AliasChoices('dept_name', 'Dept_Name'))

class DepartmentUpdate(BaseModel):
    """
    Department update request body model
    - Same fields and alias rules as creation model
    """
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_ID'))
    dept_name: str = Field(..., validation_alias=AliasChoices('dept_name', 'Dept_Name'))

class DepartmentDelete(BaseModel):
    """
    Department deletion request body model
    - Compatible with `dept_no`/`Dept_ID` and `dept_name`/`Dept_Name`
    """
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_ID'))

@router.get('/dept/list', tags=['Departments'])
async def get_dept_list(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
    Dept_ID: str | None = Query(None, description="Optional"),
    Dept_Name: str | None = Query(None, description="Optional"),
):
    """
    Obtain department information and feed to the frontend.
    """
    return db_dept_list(**locals())

@router.post('/departments/addition', tags=['Departments'])
async def add_dept(payload: DepartmentCreate = Body(..., description="Department creation information, pass as JSON")):
    """
    Create a new department.
    """
    return db_add_dept(Dept_ID=payload.dept_no, Dept_Name=payload.dept_name)

@router.put('/departments/update', tags=['Departments'])
async def update_dept(payload: DepartmentUpdate = Body(..., description="Department update information, pass as JSON")):
    """
    Update department information.
    """
    return db_update_dept(Dept_ID=payload.dept_no, Dept_Name=payload.dept_name)

@router.delete('/departments/deletion', tags=['Departments'])
async def delete_dept(payload: DepartmentDelete = Body(..., description="Department deletion information, pass as JSON")):
    """
    Delete department record.
    """
    return db_del_dept(Dept_ID=payload.dept_no)

@router.get('/departments/detail', tags=['Departments'])
async def get_dept_info(Dept_ID: str = Query(..., description="Mandatory")):
    """
    Obtain department information by department ID.
    """
    return db_get_dept_info(Dept_ID)