from fastapi import APIRouter, Query
from app.db.example import db_get_emp_list

router = APIRouter()

# 较简单的写法。下方的注释是更复杂的写法，可以提供更多的能力。
# 第一行定义接口。把下方的方法包装成接口提供给前端调用。
# get的第一个参数是接口地址。如下面的例子。启动服务后调用 http://localhost:8000/employees/list 即可调用该接口（调用get_employees_list方法）
# tags是接口分类名称。自定义一个即可
# get_employees_list方法接收的参数就是前端要传递的参数
@router.get('/employees/list', tags=['employees'])
async def get_employees_list(pageNo, pageSize, emp_no, birth_date, hire_date, name, gender):
    return db_get_emp_list(pageNo, pageSize, emp_no, birth_date, hire_date, name, gender)

# 以下复杂的写法可以提供参数约束、注释功能。
# @router.get('/employees/list', tags=['employees'])
# async def get_employees_list(
#     pageNo: int = Query(..., description="页码，必填"),
#     pageSize: int = Query(..., description="每页条数，必填"),
#     emp_no: int | None = Query(None, description="员工编号，非必填"),
#     birth_date: str | None = Query(None, description="出生日期，非必填"),
#     hire_date: str | None = Query(None, description="入职日期，非必填"),
#     name: str | None = Query(None, description="姓名，非必填"),
#     gender: str | None = Query(None, description="性别，非必填"),
# ):
#     """
#     获取员工列表：将入参原样透传给数据库查询函数。
#     - 必填：pageNo, pageSize
#     - 非必填：emp_no, birth_date, hire_date, name, gender
#     """
#     return db_get_emp_list(**locals())