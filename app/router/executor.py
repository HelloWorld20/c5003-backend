from fastapi import APIRouter, HTTPException
# from sqlalchemy import text, create_engine
from app.db.executor import executor

router = APIRouter()

@router.get("/exec", tags=["exec"])
async def get_dept_name(sql):
    try:
        return executor(sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))