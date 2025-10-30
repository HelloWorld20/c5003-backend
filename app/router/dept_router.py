from fastapi import APIRouter, Query
# from sqlalchemy import text, create_engine
from app.db.dept_db import db_dept_list, db_add_dept, db_update_dept, db_del_dept

router = APIRouter()

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
async def add_dept(
    Dept_ID: str = Query(..., description="Mandatory"),
    Dept_Name: str = Query(..., description="Mandatory"),
):
    """
    Add a department.
    """
    return db_add_dept(Dept_ID=Dept_ID, Dept_Name=Dept_Name)

@router.put('/departments/update', tags=['Departments'])
async def update_dept(
    Dept_ID: str = Query(..., description="Mandatory"),
    Dept_Name: str = Query(..., description="Mandatory"),
):
    """
    Update department info.
    """
    return db_update_dept(Dept_ID=Dept_ID, Dept_Name=Dept_Name)

@router.delete('/departments/deletion', tags=['Departments'])
async def delete_dept(Dept_ID: str, Dept_Name: str):
    """
    Delete department records.
    """
    return db_del_dept(Dept_ID=Dept_ID, Dept_Name=Dept_Name)
