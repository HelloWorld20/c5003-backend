from sqlalchemy import text
from .init import engine
from datetime import date, timedelta
from typing import Optional


# 跟踪部门间调动（内部流动模式分析）
def db_get_transfers(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 100):
    """
    查询在指定时间段内发生的部门间调动记录。

    参数:
      start_date: 开始日期，格式 'YYYY-MM-DD'，若为 None 则默认为 90 天前。
      end_date: 结束日期，格式 'YYYY-MM-DD'，若为 None 则默认为今天。
      limit: 返回条数上限。

    返回:
      列表，每项包含 emp_no, first_name, last_name, from_dept, to_dept, from_dept_name, to_dept_name, transfer_date
    """
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.fromisoformat(end_date) - timedelta(days=90)).isoformat()

    sql = """
    SELECT d_new.emp_no, e.first_name, e.last_name,
           d_old.dept_no AS from_dept, d_new.dept_no AS to_dept,
           do.dept_name AS from_dept_name, dn.dept_name AS to_dept_name,
           d_new.from_date AS transfer_date
    FROM dept_emp d_new
    JOIN employees e ON e.emp_no = d_new.emp_no
    JOIN dept_emp d_old ON d_old.emp_no = d_new.emp_no
      AND d_old.from_date = (
          SELECT MAX(from_date) FROM dept_emp de2
          WHERE de2.emp_no = d_new.emp_no AND de2.from_date < d_new.from_date
      )
    LEFT JOIN departments do ON do.dept_no = d_old.dept_no
    LEFT JOIN departments dn ON dn.dept_no = d_new.dept_no
    WHERE d_new.from_date BETWEEN :start_date AND :end_date
      AND d_old.dept_no != d_new.dept_no
    ORDER BY d_new.from_date DESC
    LIMIT :limit
    """

    with engine.connect() as conn:
        result = conn.execute(text(sql), {"start_date": start_date, "end_date": end_date, "limit": limit})

        if result.returns_rows:
            return result.mappings().all()
        else:
            return {"rowcount": result.rowcount}
