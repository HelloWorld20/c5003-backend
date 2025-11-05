from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.dept_emp_db import db_dept_emp_list, db_add_dept_emp, db_update_dept_emp, db_del_dept_emp

router = APIRouter()

class DeptEmpCreate(BaseModel):
    """
    部门员工创建请求体模型
    - 字段别名兼容：`emp_no/dept_no/from_date/to_date` 与 `Employee_ID/Dept_Number/From_Date/To_Date`
    - `to_date` 可选，缺省统一为 `'9999-01-01'`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptEmpUpdate(BaseModel):
    """
    部门员工更新请求体模型
    - 更新指定记录的结束日期（也可用于调整部门/起止日期）
    - 所有字段必填以唯一定位记录
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_Number'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str = Field(..., validation_alias=AliasChoices('to_date', 'To_Date'))

class DeptEmpDelete(BaseModel):
    """
    部门员工删除请求体模型
    - 兼容两套字段命名：`emp_no/dept_no` 与 `Employee_ID/Dept_Number`
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
async def add_dept_emp(payload: DeptEmpCreate = Body(..., description="部门员工创建信息，按 JSON 传入")):
    """
    新增部门员工记录。
    - 请求体：兼容 `emp_no/dept_no/from_date/to_date` 与 `Employee_ID/Dept_Number/From_Date/To_Date`
    - 未提供 `to_date` 时默认 `'9999-01-01'`
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_dept_emp(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/dept_emp/update', tags=['Department Employees'])
async def update_dept_emp(payload: DeptEmpUpdate = Body(..., description="部门员工更新信息，按 JSON 传入")):
    """
    更新员工的部门归属与起止日期（常用于更新 `to_date`）。
    - 请求体：兼容两套字段命名，避免 422
    """
    return db_update_dept_emp(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no, From_Date=payload.from_date, To_Date=payload.to_date)

@router.delete('/dept_emp/deletion', tags=['Department Employees'])
async def delete_dept_emp(payload: DeptEmpDelete = Body(..., description="部门员工删除信息，按 JSON 传入")):
    """
    删除部门员工记录。
    - 请求体：兼容 `emp_no/dept_no` 与 `Employee_ID/Dept_Number`
    """
    return db_del_dept_emp(Employee_ID=payload.emp_no, Dept_Number=payload.dept_no)