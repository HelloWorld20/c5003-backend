from sqlalchemy import text
from .init import engine
from datetime import date, timedelta
from typing import Optional


# 跟踪部门间调动（内部流动模式分析）
def db_get_transfers(pageNo: int = 1, pageSize: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 100):
    """
    查询在指定时间段内发生的部门间调动记录。

    参数:
        pageNo: 页码（从1开始，默认1）
        pageSize: 每页条数（默认10）
        start_date: 开始日期，格式 'YYYY-MM-DD'，若为 None 则默认为 90 天前。
        end_date: 结束日期，格式 'YYYY-MM-DD'，若为 None 则默认为今天。

    返回:
      字典：{"data": [...], "page": pageNo, "page_size": pageSize, "total": total}
      total 为匹配的记录数上限（最多 100）
    """
    # 参数保护
    if pageNo < 1:
        pageNo = 1  
    if pageSize < 1:
        pageSize = 10

    # 计算默认的时间窗口
    if end_date is None:
        end_date = date.today().isoformat()
    if start_date is None:
        start_date = (date.fromisoformat(end_date) - timedelta(days=90)).isoformat()

    TOTAL_CAP = 100

    # 先计算匹配的总数（不超过 TOTAL_CAP）
    count_sql = """
    SELECT COUNT(*) AS cnt FROM (
        SELECT d_new.emp_no
        FROM dept_emp d_new
        JOIN dept_emp d_old ON d_old.emp_no = d_new.emp_no
        AND d_old.from_date = (
          SELECT MAX(from_date) FROM dept_emp de2
          WHERE de2.emp_no = d_new.emp_no AND de2.from_date < d_new.from_date
        )
        WHERE d_new.from_date BETWEEN :start_date AND :end_date
        AND d_old.dept_no != d_new.dept_no
    ) AS sub
    """

    with engine.connect() as conn:
        cnt_result = conn.execute(text(count_sql), {"start_date": start_date, "end_date": end_date})
        cnt_row = cnt_result.fetchone()
        total_matches = int(cnt_row[0]) if cnt_row is not None else 0
        total = total_matches if total_matches <= TOTAL_CAP else TOTAL_CAP

        # 计算 offset 与 limit，保证不超过 TOTAL_CAP
        offset = (pageNo - 1) * pageSize
        if offset >= total:
            return {"data": [], "page": pageNo, "page_size": pageSize, "total": total}

        remaining = total - offset
        fetch_limit = pageSize if pageSize <= remaining else remaining

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
    LIMIT :limit OFFSET :offset
    """

        result = conn.execute(text(sql), {"start_date": start_date, "end_date": end_date, "limit": fetch_limit, "offset": offset})

        if result.returns_rows:
            data = result.mappings().all()
            return {"data": data, "page": pageNo, "page_size": pageSize, "total": total}
        else:
            return {"data": [], "page": pageNo, "page_size": pageSize, "total": total}

