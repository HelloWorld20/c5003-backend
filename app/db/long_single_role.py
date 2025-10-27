from sqlalchemy import text
from .init import engine
from datetime import date, timedelta
from typing import Optional


# 识别长时间处于同一职务的员工（候选人用于培训/晋升评估）

def db_get_long_single_role(pageNo: int = 1, pageSize: int = 10, min_days: int = 1095, as_of_date: Optional[str] = None):
	"""
	查询在同一 title 下持续时间超过 min_days 的员工（支持分页，每页 pageSize，最大总数 100）。

	参数:
		pageNo: 页码（从1开始，默认1）
		pageSize: 每页条数（默认10）
		min_days: 最少天数阈值（默认 1095 天 = 约 3 年）
		as_of_date: 计算截止日期，格式 'YYYY-MM-DD'，默认今天

	返回:
		字典：{"data": [...], "page": pageNo, "page_size": pageSize, "total": total}
		total 为匹配的记录数上限（最多 100）
	"""

	# 参数保护
	if pageNo < 1:
		pageNo = 1
	if pageSize < 1:
		pageSize = 10

	if as_of_date is None:
		as_of_date = date.today().isoformat()

	TOTAL_CAP = 100

	# 先计算匹配的总数（不超过 TOTAL_CAP）
	count_sql = """
	SELECT COUNT(*) AS cnt FROM (
	  SELECT emp_no, MAX(from_date) AS last_from
	  FROM titles
	  GROUP BY emp_no
	  HAVING DATEDIFF(:as_of_date, MAX(from_date)) >= :min_days
	) AS sub
	"""

	with engine.connect() as conn:
		cnt_result = conn.execute(text(count_sql), {"as_of_date": as_of_date, "min_days": min_days})
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
	SELECT t_latest.emp_no, e.first_name, e.last_name,
	       t_latest.title AS current_title, t_latest.from_date AS title_start_date,
	       DATEDIFF(:as_of_date, t_latest.from_date) AS days_in_role
	FROM (
	  SELECT t.emp_no, t.title, t.from_date
	  FROM titles t
	  WHERE (t.emp_no, t.from_date) IN (
	    SELECT emp_no, MAX(from_date) FROM titles GROUP BY emp_no
	  )
	) AS t_latest
	JOIN employees e ON e.emp_no = t_latest.emp_no
	WHERE DATEDIFF(:as_of_date, t_latest.from_date) >= :min_days
	ORDER BY days_in_role DESC
	LIMIT :limit OFFSET :offset
	"""

		result = conn.execute(text(sql), {"as_of_date": as_of_date, "min_days": min_days, "limit": fetch_limit, "offset": offset})

		if result.returns_rows:
			data = result.mappings().all()
			return {"data": data, "page": pageNo, "page_size": pageSize, "total": total}
		else:
			return {"rowcount": result.rowcount}

