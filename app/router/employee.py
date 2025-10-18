from fastapi import APIRouter, Query, Body
# from sqlalchemy import text, create_engine
from app.db.employee import db_get_emp_list, db_add_emp, db_del_emp, db_update_emp

router = APIRouter()

@router.get('/employees/list', tags=['employees'])
async def get_employees_list(
    page: int = Query(..., description="页码，必填"),
    pageSize: int = Query(..., description="每页条数，必填"),
    emp_no: int | None = Query(None, description="员工编号，非必填"),
    birth_date_start: str | None = Query(None, description="出生开始日期，非必填"),
    birth_date_end: str | None = Query(None, description="出生结束日期，非必填"),
    hire_date_start: str | None = Query(None, description="入职开始日期，非必填"),
    hire_date_end: str | None = Query(None, description="入职结束日期，非必填"),
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
async def add_employee(
    gender: str = Body(..., description="性别，必填"),
    birth_date: str = Body(..., description="出生日期，必填"),
    hire_date: str = Body(..., description="入职日期，必填"),
    name: str = Body(..., description="姓名，必填")
):
    """
    添加员工：创建新的员工记录。
    - 请求体参数：gender, birth_date, hire_date, name
    """
    return db_add_emp(gender=gender, birth_date=birth_date, hire_date=hire_date, name=name)

@router.put('/employees/{emp_no}', tags=['employees'])
async def update_employee(
    emp_no: int,
    hire_date: str = Query(..., description="入职日期，必填"),
    name: str = Query(..., description="姓名，必填"),
):
    """
    更新员工信息：根据员工编号更新员工的入职日期和姓名。
    - 路径参数：emp_no (员工编号)
    - 必填：hire_date, name
    """
    return db_update_emp(emp_no=emp_no, hire_date=hire_date, name=name)

@router.delete('/employees/{emp_no}', tags=['employees'])
async def delete_employee(emp_no: int):
    """
    删除员工：根据员工编号删除员工记录。
    - 路径参数：emp_no (员工编号)
    """
    return db_del_emp(emp_no=emp_no)