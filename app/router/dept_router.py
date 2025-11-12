from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field, AliasChoices
# from sqlalchemy import text, create_engine
from app.db.dept_db import db_dept_list, db_add_dept, db_update_dept, db_del_dept, db_get_dept_info

router = APIRouter()

class DepartmentCreate(BaseModel):
    """
    部门创建请求体模型
    - 支持字段别名兼容：`dept_no`/`Dept_ID` 与 `dept_name`/`Dept_Name`
    - 目的：防止前端以不同命名风格传参导致 422 校验错误
    """
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_ID'))
    dept_name: str = Field(..., validation_alias=AliasChoices('dept_name', 'Dept_Name'))

class DepartmentUpdate(BaseModel):
    """
    部门更新请求体模型
    - 与创建模型一致的字段与别名规则
    """
    dept_no: str = Field(..., validation_alias=AliasChoices('dept_no', 'Dept_ID'))
    dept_name: str = Field(..., validation_alias=AliasChoices('dept_name', 'Dept_Name'))

class DepartmentDelete(BaseModel):
    """
    部门删除请求体模型
    - 兼容 `dept_no`/`Dept_ID` 与 `dept_name`/`Dept_Name`
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
async def add_dept(payload: DepartmentCreate = Body(..., description="部门创建信息，按 JSON 传入")):
    """
    创建部门。
    - 请求体：兼容 `dept_no/dept_name` 与 `Dept_ID/Dept_Name`
    """
    return db_add_dept(Dept_ID=payload.dept_no, Dept_Name=payload.dept_name)

@router.put('/departments/update', tags=['Departments'])
async def update_dept(payload: DepartmentUpdate = Body(..., description="部门更新信息，按 JSON 传入")):
    """
    更新部门信息。
    - 请求体：兼容 `dept_no/dept_name` 与 `Dept_ID/Dept_Name`
    """
    return db_update_dept(Dept_ID=payload.dept_no, Dept_Name=payload.dept_name)

@router.delete('/departments/deletion', tags=['Departments'])
async def delete_dept(payload: DepartmentDelete = Body(..., description="部门删除信息，按 JSON 传入")):
    """
    删除部门记录。
    - 请求体：兼容 `dept_no/dept_name` 与 `Dept_ID/Dept_Name`
    """
    return db_del_dept(Dept_ID=payload.dept_no)

@router.get('/departments/detail', tags=['Departments'])
async def get_dept_info(Dept_ID: str = Query(..., description="Mandatory")):
    """
    Obtain department information by department ID.
    """
    return db_get_dept_info(Dept_ID)