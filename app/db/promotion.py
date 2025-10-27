from sqlalchemy import text
from .init import engine
from datetime import date, timedelta
from typing import Optional


# 追踪内部流动（部门之间的变动）
def db_get_internal_mobility(pageNo: int = 1, pageSize: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    查询在指定时间段内发生部门变动的员工记录。

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
           d_new.from_date AS move_date
    FROM dept_emp d_new
    JOIN employees e ON e.emp_no = d_new.emp_no
    JOIN dept_emp d_old ON d_old.emp_no = d_new.emp_no
      AND d_old.from_date = (
          SELECT MAX(from_date) FROM dept_emp de2
          WHERE de2.emp_no = d_new.emp_no AND de2.from_date < d_new.from_date
      )
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


# 识别近期晋升的员工（基于 titles 表的职称变更）
def db_get_recent_promotions(pageNo: int = 1, pageSize: int = 10, window_days: int = 90):
    """
    查询最近 window_days 天内发生职称变化（视为晋升）的员工。

    实现说明：
    - 视为晋升的规则为 titles 表中出现了新的 title 且与前一个 title 不同。
    - 使用 titles.from_date 来判断晋升时间。

    参数:
        pageNo: 页码（从1开始，默认1）
        pageSize: 每页条数（默认10）
        window_days: 向前查询的天数窗口（默认 90 天）

    返回:
      字典：{"data": [...], "page": pageNo, "page_size": pageSize, "total": total}
    """
    # 参数保护
    if pageNo < 1:
        pageNo = 1  
    if pageSize < 1:
        pageSize = 10

    # 计算默认的时间窗口
    cutoff = (date.today() - timedelta(days=window_days)).isoformat()

    TOTAL_CAP = 100

    # 先计算匹配的总数（不超过 TOTAL_CAP）
    count_sql = """
    SELECT COUNT(*) AS cnt FROM (
        SELECT t_new.emp_no
        FROM titles t_new
        JOIN titles t_old ON t_old.emp_no = t_new.emp_no
          AND t_old.from_date = (
              SELECT MAX(from_date) FROM titles t2
              WHERE t2.emp_no = t_new.emp_no AND t2.from_date < t_new.from_date
          )
        WHERE t_new.from_date >= :cutoff_date
          AND t_old.title != t_new.title
    ) AS sub
    """
    
    with engine.connect() as conn:
        cnt_result = conn.execute(text(count_sql), {"cutoff_date": cutoff})
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
    SELECT t_new.emp_no, e.first_name, e.last_name,
           t_old.title AS old_title, t_new.title AS new_title,
           t_new.from_date AS promotion_date
    FROM titles t_new
    JOIN employees e ON e.emp_no = t_new.emp_no
    JOIN titles t_old ON t_old.emp_no = t_new.emp_no
      AND t_old.from_date = (
          SELECT MAX(from_date) FROM titles t2
          WHERE t2.emp_no = t_new.emp_no AND t2.from_date < t_new.from_date
      )
    WHERE t_new.from_date >= :cutoff_date
      AND t_old.title != t_new.title
    ORDER BY t_new.from_date DESC
    LIMIT :limit OFFSET :offset
    """

        result = conn.execute(text(sql), {"cutoff_date": cutoff, "limit": fetch_limit, "offset": offset})

        if result.returns_rows:
            data = result.mappings().all()
            return {"data": data, "page": pageNo, "page_size": pageSize, "total": total}
        else:
            return {"data": [], "page": pageNo, "page_size": pageSize, "total": total}
