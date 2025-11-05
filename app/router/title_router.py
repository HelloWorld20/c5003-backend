from fastapi import APIRouter, Query, Body, HTTPException
from pydantic import BaseModel, Field, AliasChoices, AliasPath
# from sqlalchemy import text, create_engine
from app.db.title_db import db_title_list, db_add_title, db_update_title, db_del_title

router = APIRouter()


class TitleUpdate(BaseModel):
    """
    职称更新请求体模型
    - 支持两种命名风格：
      - 前端常用：`emp_no`, `title`, `from_date`, `to_date`
      - 旧接口风格：`Employee_ID`, `Title`, `From_Date`, `To_Date`
    - 通过 `validation_alias` 同时兼容两套字段名，避免 422 校验错误
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
    职称创建请求体模型
    - 兼容两套命名：`emp_no/title/from_date/to_date` 与 `Employee_ID/Title/From_Date/To_Date`
    - `to_date` 可选，缺省为 `'9999-01-01'`
    """
    emp_no: int = Field(..., validation_alias=AliasChoices('emp_no', 'Employee_ID'))
    title: str = Field(..., validation_alias=AliasChoices('title', 'Title'))
    from_date: str = Field(..., validation_alias=AliasChoices('from_date', 'From_Date'))
    to_date: str | None = Field(None, validation_alias=AliasChoices('to_date', 'To_Date'))

class TitleDelete(BaseModel):
    """
    职称删除请求体模型
    - 兼容两套字段命名：`emp_no/title` 与 `Employee_ID/Title`
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
async def add_title(payload: TitleCreate = Body(..., description="职称创建信息，按 JSON 传入")):
    """
    新增员工职称记录。
    - 请求体：兼容两套字段命名，避免 422
    - 未提供 `to_date` 时默认 `'9999-01-01'`
    """
    effective_to_date = '9999-01-01' if payload.to_date is None else payload.to_date
    return db_add_title(Employee_ID=payload.emp_no, Title=payload.title, From_Date=payload.from_date, To_Date=effective_to_date)

@router.put('/titles/update', tags=['Titles'])
async def update_title(payload: dict = Body(..., description="职称更新信息，按 JSON 传入（可嵌套 payload）")):
    """
    更新员工职称的结束日期。
    - 接受任意 JSON 结构，不使用 Pydantic 强校验，避免 422。
    - 兼容字段命名与结构：
      - 顶层：`emp_no/title/from_date/to_date` 或 `Employee_ID/Title/From_Date/To_Date`
      - 包裹：`{"payload": { ...同上... }}`
    - 根据 `emp_no + title + from_date` 定位记录，更新其 `to_date`。
    """
    # 允许 payload 外层包裹
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
        # 返回 400 而非 422，提示缺失字段，避免 Pydantic 层拦截
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
async def delete_title(payload: TitleDelete = Body(..., description="职称删除信息，按 JSON 传入")):
    """
    删除员工职称记录。
    - 请求体：兼容 `emp_no/title` 与 `Employee_ID/Title`
    """
    return db_del_title(Employee_ID=payload.emp_no, Title=payload.title)
