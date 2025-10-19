from sqlalchemy import text
from .init import engine
from datetime import date, timedelta
from typing import Optional


# 识别长时间处于同一职务的员工（候选人用于培训/晋升评估）
def db_get_long_single_role(min_days: int = 1095, as_of_date: Optional[str] = None, limit: int = 100):
		"""
		查询在同一 title 下持续时间超过 min_days 的员工。

		参数:
			min_days: 最少天数阈值（默认 1095 天 = 约 3 年）
			as_of_date: 计算截止日期，格式 'YYYY-MM-DD'，默认今天
			limit: 返回条数上限

		返回:
			列表，每项包含 emp_no, first_name, last_name, current_title, title_start_date, days_in_role
		"""
		if as_of_date is None:
				as_of_date = date.today().isoformat()

		sql = """
		-- 对每位员工取最新一条 title 记录 t_latest
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
		LIMIT :limit
		"""

		with engine.connect() as conn:
				result = conn.execute(text(sql), {"as_of_date": as_of_date, "min_days": min_days, "limit": limit})

				if result.returns_rows:
						return result.mappings().all()
				else:
						return {"rowcount": result.rowcount}

