from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.salary_db import db_salary_list, db_add_salary, db_update_salary, db_del_salary

router = APIRouter()

class SalaryCreate(BaseModel):
    """
    薪资创建请求体模型
    - 兼容两套字段命名：
      - 前端常用：`emp_no`, `salary`, `from_date`, `to_date`
      - 旧接口风格：`Employee_ID`, `Salary`, `From_Date`, `To_Date`
    - `to_date` 可选，缺省时路由层统一为 `'9999-01-01'`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    salary: int = Field(..., validation_alias=AliasChoices('salary', 'Salary'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class SalaryUpdate(BaseModel):
    """
    薪资更新请求体模型
    - 用于更新某条薪资记录的结束日期
    - 所有字段必填以唯一定位记录
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    salary: int = Field(..., validation_alias=AliasChoices('salary', 'Salary'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str = Field(..., validation_alias=AliasChoices('to_date', 'To_Date'))

class SalaryDelete(BaseModel):
    """
    薪资删除请求体模型
    - 兼容两套字段命名：`emp_no/salary` 与 `Employee_ID/Salary`
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
async def add_salary(payload: SalaryCreate = Body(..., description="薪资创建信息，按 JSON 传入")):
    """
    新增薪资记录。
    - 请求体：兼容 `emp_no/salary/from_date/to_date` 与 `Employee_ID/Salary/From_Date/To_Date`
    - 若 `to_date` 未提供，默认使用 `'9999-01-01'`
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_salary(Employee_ID=payload.emp_no, Salary=payload.salary, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/salary/update', tags=['Salaries'])
async def update_dept_emp(payload: SalaryUpdate = Body(..., description="薪资更新信息，按 JSON 传入")):
    """
    更新员工薪资记录的结束日期。
    - 请求体：兼容两套字段命名，避免 422
    """
    return db_update_salary(Employee_ID=payload.emp_no, Salary=payload.salary, From_Date=payload.from_date, To_Date=payload.to_date)

@router.delete('/salary/deletion', tags=['Salaries'])
async def delete_salary(payload: SalaryDelete = Body(..., description="薪资删除信息，按 JSON 传入")):
    """
    删除员工薪资记录。
    - 请求体：兼容 `emp_no/salary` 与 `Employee_ID/Salary`
    """
    return db_del_salary(Employee_ID=payload.emp_no, Salary=payload.salary)