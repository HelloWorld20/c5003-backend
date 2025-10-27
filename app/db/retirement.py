from sqlalchemy import text
from .init import engine
from typing import Optional
from datetime import date


def db_get_retirement_candidates(dept_no: Optional[str] = None, retirement_age: int = 65, limit: int = 100, page: int = 1):
    """
    Identify employees nearing retirement age based on configurable retirement age.
    
    Parameters:
        dept_no: Department number (None means all departments)
        retirement_age: Retirement age threshold (default 65)
        limit: Number of records per page (default 100)
        page: Page number, starting from 1 (default 1)
    
    Returns:
        Dictionary containing:
        - data: List of employees with birth year <= (current year - retirement_age) and currently employed
        - total_count: Total number of matching records
        - page: Current page number
        - page_size: Records per page
        - total_pages: Total number of pages
    """
    current_year = date.today().year
    birth_year_threshold = current_year - retirement_age
    
    # Calculate OFFSET
    offset = (page - 1) * limit
    
    # SQL for total count
    count_sql = """
    SELECT COUNT(DISTINCT e.emp_no) AS total
    FROM employees e
    JOIN dept_emp d ON e.emp_no = d.emp_no
    WHERE YEAR(e.birth_date) <= :birth_year_threshold
      AND d.to_date = '9999-01-01'
      AND (:dept_no IS NULL OR d.dept_no = :dept_no)
    """
    
    # Order by department, then hierarchy level, then employee number for optimal indexed performance
    data_sql = """
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
    LIMIT :limit OFFSET :offset
    """
    
    with engine.connect() as conn:
        # Get total count
        count_result = conn.execute(
            text(count_sql),
            {
                "birth_year_threshold": birth_year_threshold,
                "dept_no": dept_no
            }
        )
        total_count = count_result.scalar() or 0
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        # Get data
        data_result = conn.execute(
            text(data_sql),
            {
                "birth_year_threshold": birth_year_threshold,
                "dept_no": dept_no,
                "limit": limit,
                "offset": offset
            }
        )
        
        if data_result.returns_rows:
            rows = data_result.mappings().all()
            return {
                "data": [dict(row) for row in rows],
                "total_count": total_count,
                "page": page,
                "page_size": limit,
                "total_pages": total_pages
            }
        else:
            return {
                "data": [],
                "total_count": 0,
                "page": page,
                "page_size": limit,
                "total_pages": 0
            }