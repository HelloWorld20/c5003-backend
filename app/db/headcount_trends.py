from sqlalchemy import text
from .init import engine
from typing import Optional




def db_get_headcount_changes_by_year(start_year: Optional[int] = None, end_year: Optional[int] = None):
    """
    Get headcount changes by year (hires + departures + net changes)
    
    Parameters:
        start_year: Start year (None means from earliest year)
        end_year: End year (None means to latest year)
    
    Returns:
        List of comprehensive headcount changes for each year
    """
    
    sql = """
    WITH hires AS (
        SELECT 
            YEAR(hire_date) AS year,
            COUNT(*) AS new_hires
        FROM employees
        WHERE (:start_year IS NULL OR YEAR(hire_date) >= :start_year)
            AND (:end_year IS NULL OR YEAR(hire_date) <= :end_year)
        GROUP BY YEAR(hire_date)
    ),
    departures AS (
        SELECT 
            YEAR(de.to_date) AS year,
            COUNT(DISTINCT de.emp_no) AS departures
        FROM dept_emp de
        WHERE de.to_date != '9999-01-01'
            AND (:start_year IS NULL OR YEAR(de.to_date) >= :start_year)
            AND (:end_year IS NULL OR YEAR(de.to_date) <= :end_year)
        GROUP BY YEAR(de.to_date)
    ),
    all_years AS (
        SELECT year FROM hires
        UNION
        SELECT year FROM departures
    )
    SELECT 
        ay.year,
        COALESCE(h.new_hires, 0) AS new_hires,
        COALESCE(d.departures, 0) AS departures,
        COALESCE(h.new_hires, 0) - COALESCE(d.departures, 0) AS net_change,
        CASE 
            WHEN COALESCE(d.departures, 0) = 0 THEN 0
            ELSE ROUND(COALESCE(d.departures, 0) * 100.0 / COALESCE(h.new_hires, 1), 2)
        END AS turnover_rate_percent
    FROM all_years ay
    LEFT JOIN hires h ON ay.year = h.year
    LEFT JOIN departures d ON ay.year = d.year
    ORDER BY ay.year
    """
    
    with engine.connect() as conn:
        result = conn.execute(
            text(sql),
            {"start_year": start_year, "end_year": end_year}
        )
        
        if result.returns_rows:
            rows = result.mappings().all()
            return [dict(row) for row in rows]
        else:
            return []

