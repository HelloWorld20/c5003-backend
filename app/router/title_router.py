from fastapi import APIRouter, Query, Body, HTTPException
from pydantic import BaseModel, Field, AliasChoices, AliasPath
# from sqlalchemy import text, create_engine
from app.db.title_db import db_title_list, db_add_title, db_update_title, db_del_title

router = APIRouter()


class TitleUpdate(BaseModel):
    """
    Title update request body model
    - Supports two naming styles:
      - Frontend common: `emp_no`, `title`, `from_date`, `to_date`
      - Legacy API style: `Employee_ID`, `Title`, `From_Date`, `To_Date`
    - Compatible with both field naming styles via `validation_alias` to avoid 422 validation errors
    """
    emp_no: int = Field(
        ...,
        validation_alias=AliasChoices(
            'emp_no', 'Employee_ID',
            AliasPath('payload', 'emp_no'), AliasPath('payload', 'Employee_ID')
        )
    )
    title: str = Field(
        ...,
        validation_alias=AliasChoices(
            'title', 'Title',
            AliasPath('payload', 'title'), AliasPath('payload', 'Title')
        )
    )
    from_date: str = Field(
        ...,
        validation_alias=AliasChoices(
            'from_date', 'From_Date',
            AliasPath('payload', 'from_date'), AliasPath('payload', 'From_Date')
        )
    )
    to_date: str = Field(
        ...,
        validation_alias=AliasChoices(
            'to_date', 'To_Date',
            AliasPath('payload', 'to_date'), AliasPath('payload', 'To_Date')
        )
    )

class TitleCreate(BaseModel):
    """
    Title creation request body model
    - Compatible with two naming styles: `emp_no/title/from_date/to_date` and `Employee_ID/Title/From_Date/To_Date`
    - `to_date` is optional, defaults to `'9999-01-01'`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    title: str = Field(..., validation_alias=AliasChoices('title', 'Title'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class TitleDelete(BaseModel):
    """
    Title deletion request body model
    - Compatible with two field naming styles: `emp_no/title` and `Employee_ID/Title`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    title: str = Field(..., validation_alias=AliasChoices('title', 'Title'))

@router.get('/titles/list', tags=['Titles'])
async def get_titles_list(
    Page_Number: int = Query(..., description="Mandatory"),
    Row_Count: int = Query(..., description="Mandatory"),
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
async def add_title(payload: TitleCreate = Body(..., description="Title creation information, pass as JSON")):
    """
    Create a new employee title record.
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_title(Employee_ID=payload.emp_no, Title=payload.title, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/titles/update', tags=['Titles'])
async def update_title(payload: dict = Body(..., description="Title update information, pass as JSON (can be nested in payload)")):
    """
    Update employee title end date.
    """
    # Allow payload to be wrapped
    data = payload.get('payload', payload) if isinstance(payload, dict) else {}

    def pick(keys: list[str]):
        for k in keys:
            if k in data and data[k] is not None:
                return data[k]
        return None

    emp_no = pick(['emp_no', 'Employee_ID'])
    title = pick(['title', 'Title'])
    from_date = pick(['from_date', 'From_Date'])
    to_date = pick(['to_date', 'To_Date'])

    missing = [name for name, val in (
        ('emp_no', emp_no), ('title', title), ('from_date', from_date), ('to_date', to_date)
    ) if val is None]

    if missing:
        # Return 400 instead of 422, indicate missing fields, avoid Pydantic layer interception
        raise HTTPException(status_code=400, detail={
            'message': 'Missing required fields',
            'missing': missing
        })

    return db_update_title(
        Employee_ID=emp_no,
        Title=title,
        From_Date=from_date,
        To_Date=to_date,
    )

@router.delete('/titles/deletion', tags=['Titles'])
async def delete_title(payload: TitleDelete = Body(..., description="Title deletion information, pass as JSON")):
    """
    Delete employee title record.
    """
    return db_del_title(Employee_ID=payload.emp_no, Title=payload.title)
