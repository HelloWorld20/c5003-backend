from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.dept_manager_db import db_dept_manager_list, db_add_dept_manager, db_update_dept_manager, db_del_dept_manager

router = APIRouter()

class DeptManagerCreate(BaseModel):
    """
    部门经理创建请求体模型
    - 字段别名兼容：`emp_no/dept_no/from_date/to_date` 与 `Employee_ID/Dept_Number/From_Date/To_Date`
    - `to_date` 可选，缺省统一为 `'9999-01-01'`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptManagerUpdate(BaseModel):
    """
    部门经理更新请求体模型
    - 所有字段必填以唯一定位记录
    - 通常用于更新 `to_date`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str = Field(..., validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptManagerDelete(BaseModel):
    """
    部门经理删除请求体模型
    - 兼容两套字段命名：`emp_no/dept_no` 与 `Employee_ID/Dept_Number`
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
    Obtain department manager information and feed to the frontend.
    """
    return db_dept_manager_list(**locals())

@router.post('/dept_manager/addition', tags=['Department Managers'])
async def add_dept_manager(payload: DeptManagerCreate = Body(..., description="部门经理创建信息，按 JSON 传入")):
    """
    新增部门经理记录。
    - 请求体：兼容两套字段命名风格
    - `to_date` 未提供时默认 `'9999-01-01'`
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_dept_manager(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/dept_manager/update', tags=['Department Managers'])
async def update_dept_manager(payload: DeptManagerUpdate = Body(..., description="部门经理更新信息，按 JSON 传入")):
    """
    更新部门经理的部门归属与起止日期（常用于更新 `to_date`）。
    - 请求体：兼容两套字段命名，避免 422
    """
    return db_update_dept_manager(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=payload.to_date)

@router.delete('/dept_manager/deletion', tags=['Department Managers'])
async def delete_dept_manager(payload: DeptManagerDelete = Body(..., description="部门经理删除信息，按 JSON 传入")):
    """
    删除部门经理记录。
    - 请求体：兼容 `emp_no/dept_no` 与 `Employee_ID/Dept_Number`
    """
    return db_del_dept_manager(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no)