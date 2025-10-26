from fastapi import APIRouter, Query
# from sqlalchemy import text, create_engine
from app.db.title_db import db_title_list, db_add_title, db_update_title, db_del_title

router = APIRouter()

@router.get('/titles/list', tags=['Titles'])
async def get_titles_list(
    Page_Number: int | None = Query(..., description="Mandatory"),
    Row_Count: int | None = Query(..., description="Mandatory"),
    Employee_ID: int | None = Query(None, description="Optional"),
    Title: str | None = Query(None, description="Optional"),
    From_Date: str | None = Query(None, description="Optional"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Obtain title information and feed to the frontend.
    """
    return db_title_list(**locals())

@router.post('/titles/addition', tags=['Titles'])
async def add_title(
    Employee_ID: int | None = Query(..., description="Mandatory"),
    Title: str | None = Query(..., description="Mandatory"),
    From_Date: str | None = Query(..., description="Mandatory"),
    To_Date: str | None = Query(None, description="Optional"),
):
    """
    Add employee title.
    """
    effective_to_date = '9999-01-01' if To_Date is None else To_Date
    return db_add_title(Employee_ID=Employee_ID, Title=Title, From_Date=From_Date, To_Date = effective_to_date)

@router.put('/titles/update', tags=['Titles'])
async def update_title(
    Employee_ID: int| None = Query(..., description="Mandatory"),
    Title: str | None = Query(..., description="Mandatory"),
    From_Date: str | None = Query(..., description="Mandatory"),
    To_Date: str | None = Query(..., description="Mandatory"),
):
    """
    Update employee title, start_date and end_date.
    """
    return db_update_title(Employee_ID=Employee_ID, Title=Title, From_Date=From_Date, To_Date=To_Date)

@router.delete('/titles/deletion', tags=['Titles'])
async def delete_title(Employee_ID: int, Title: str):
    """
    Delete employee records.
    """
    return db_del_title(Employee_ID=Employee_ID, Title=Title)