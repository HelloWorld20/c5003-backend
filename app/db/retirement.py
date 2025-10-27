from sqlalchemy import text
from app.db.init import engine
from typing import Optional
from datetime import date

def db_get_retirement_candidates(dept_no: Optional[str] = None, retirement_age: int = 65, limit: int = 100):
    """
    Identify employees nearing retirement age based on configurable retirement age.
    
    Parameters:
        dept_no: Department number (None means all departments)
        retirement_age: Retirement age threshold (default 65)
        limit: Limit of returned records (default 100)
    
    Returns:
        List of employees with birth year <= (current year - retirement_age) and currently employed
    """
    current_year = date.today().year
    birth_year_threshold = current_year - retirement_age

    sql = """
    SELECT 
        e.emp_no,
        e.first_name,
        e.last_name,
        e.birth_date,
        e.gender,
        e.hire_date,
        d.dept_no,
        dp.dept_name,
        t.title
    FROM employees e
    JOIN dept_emp d ON e.emp_no = d.emp_no
    JOIN departments dp ON d.dept_no = dp.dept_no
    LEFT JOIN titles t ON e.emp_no = t.emp_no AND t.to_date = '9999-01-01'
    WHERE YEAR(e.birth_date) <= :birth_year_threshold
      AND d.to_date = '9999-01-01'
      AND (:dept_no IS NULL OR d.dept_no = :dept_no)
    ORDER BY e.birth_date ASC
    LIMIT :limit
    """

    with engine.connect() as conn:
        result = conn.execute(
            text(sql),
            {
                "birth_year_threshold": birth_year_threshold,
                "dept_no": dept_no,
                "limit": limit
            }
        )

        if result.returns_rows:
            rows = result.mappings().all()
            return [dict(row) for row in rows]
        else:
            return []