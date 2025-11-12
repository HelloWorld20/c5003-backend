from fastapi import APIRouter, Query, Body
from pydantic import BaseModel
# from sqlalchemy import text, create_engine
from app.db.employee import db_get_emp_list, db_add_emp, db_del_emp, db_update_emp, get_emp_info

router = APIRouter()


class EmployeeUpdate(BaseModel):
    """
    员工更新请求体模型
    - 可选字段：`birth_date`, `hire_date`, `gender`, `name`, `first_name`, `last_name`, `emp_no`
    - 支持同时传入 `name` 或者 `first_name` + `last_name`，路由层会进行合并
    """
    emp_no: int | None = None
    birth_date: str | None = None
    hire_date: str | None = None
    gender: str | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    dept_no: str | None = None
    title: str | None = None
    salary: int | None = None


class EmployeeCreate(BaseModel):
    """
    员工创建请求体模型
    - 必填字段：`birth_date`, `hire_date`, `gender`
    - 可选字段：`name` 或者 `first_name` + `last_name`
    - 若同时提供 `name` 与 `first_name/last_name`，优先使用 `name`
    """
    birth_date: str
    hire_date: str
    gender: str
    emp_no: int | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    dept_no: str | None = None
    salary: int | None = None
    title: str | None = None



@router.get('/employees/list', tags=['employees'])
async def get_employees_list(
    page: int = Query(..., description="页码，必填"),
    pageSize: int = Query(..., description="每页条数，必填"),
    emp_no: int | None = Query(None, description="员工编号，非必填"),
    birth_date: str | None = Query(None, description="出生日期，非必填"),
    hire_date: str | None = Query(None, description="入职日期，非必填"),
    name: str | None = Query(None, description="姓名，非必填"),
    gender: str | None = Query(None, description="性别，非必填"),
):
    """
    获取员工列表：将入参原样透传给数据库查询函数。
    - 必填：pageNo, pageSize
    - 非必填：emp_no, birth_date, hire_date, name, gender
    """
    return db_get_emp_list(**locals())

@router.post('/employees', tags=['employees'])
async def add_employee(payload: EmployeeCreate = Body(..., description="员工创建信息，请按 JSON 传入")):
    """
    添加员工：创建新的员工记录。
    - 请求体：`birth_date`, `hire_date`, `gender` 必填；`name` 或 `first_name` + `last_name` 可选
    - 说明：若同时提供 `name` 与 `first_name/last_name`，优先使用 `name`
    """
    # 规范化姓名：优先使用 name；否则拼接 first_name + last_name
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

@router.put('/employees/{emp_no}', tags=['employees'])
async def update_employee(
    emp_no: int,
    payload: EmployeeUpdate = Body(..., description="员工更新信息，请按 JSON 传入")
):
    """
    更新员工信息：根据员工编号更新员工的基础资料。
    - 路径参数：`emp_no`（员工编号）
    - 请求体：可选字段 `birth_date`, `hire_date`, `gender`, `name` 或 `first_name` + `last_name`
    - 说明：若同时提供 `name` 与 `first_name/last_name`，优先使用 `name`
    """
    # 将 name 规范化为“名 + 空格 + 姓”的形式；若未提供则保持为 None
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

@router.delete('/employees/{emp_no}', tags=['employees'])
async def delete_employee(emp_no: int):
    """
    删除员工：根据员工编号删除员工记录。
    - 路径参数：emp_no (员工编号)
    """
    return db_del_emp(emp_no=emp_no)

@router.get('/employees/{emp_no}', tags=['employees'])
async def get_employee_info(emp_no: int):
    """
    获取员工信息：根据员工编号查询员工的详细信息。
    - 路径参数：emp_no (员工编号)
    """
    return get_emp_info(emp_no=emp_no)