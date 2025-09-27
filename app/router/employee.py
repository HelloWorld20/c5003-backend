from fastapi import APIRouter, Query
# from sqlalchemy import text, create_engine
from app.db.employee import db_get_emp_list

router = APIRouter()

@router.get('/employees/list', tags=['employees'])
async def get_employees_list(
    pageNo: int = Query(..., description="页码，必填"),
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

# @router.get("/users/me", tags=["dept"])
# async def read_user_me():
#     return {"username": "fakecurrentuser"}

# @router.get("/dept_name", tags=["dept"])
# async def get_dept_name():
#     """
#     dept
#     """
#     # 数据库连接配置
#     return db_get_dept_name()

# @router.get('/dept', tags=['dept'])
# async def get_dept():
#     return db_get_dept()