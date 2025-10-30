from fastapi import APIRouter, Query
# from sqlalchemy import text, create_engine
from app.db.dept_manager_db import db_dept_manager_list, db_add_dept_manager, db_update_dept_manager, db_del_dept_manager

router = APIRouter()

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
async def add_dept_manager(
    Employee_ID: int = Query(..., description="Mandatory"),
    Dept_Number: str = Query(..., description="Mandatory"),
    From_Date: str = Query(..., description="Mandatory"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Add department manager.
    """
    effective_to_date = '9999-01-01' if To_Date is None else To_Date
    return db_add_dept_manager(Employee_ID=Employee_ID, Dept_Number=Dept_Number, From_Date=From_Date, To_Date = effective_to_date)

@router.put('/dept_manager/update', tags=['Department Managers'])
async def update_dept_manager(
    Employee_ID: int = Query(..., description="Mandatory"),
    Dept_Number: str = Query(..., description="Mandatory"),
    From_Date: str = Query(..., description="Mandatory"),
    To_Date: str = Query(..., description="Mandatory"),
):
    """
    Update manager department, start_date and end_date.
    """
    return db_update_dept_manager(Employee_ID=Employee_ID, Dept_Number=Dept_Number, From_Date=From_Date, To_Date=To_Date)

@router.delete('/dept_manager/deletion', tags=['Department Managers'])
async def delete_dept_manager(Employee_ID: int, Dept_Number: str):
    """
    Delete department employee.
    """
    return db_del_dept_manager(Employee_ID=Employee_ID, Dept_Number=Dept_Number)