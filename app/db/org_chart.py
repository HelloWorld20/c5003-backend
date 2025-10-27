from sqlalchemy import text
from .init import engine
from typing import Optional


def db_get_organizational_chart(dept_no: Optional[str] = None, limit: int = 100, page: int = 1):
    """
    Build organizational chart using recursive CTE with pagination
    
    Parameters:
        dept_no: Department number (None means all departments)
        limit: Number of records per page (default 100)
        page: Page number, starting from 1 (default 1)
    
    Returns:
        Dictionary containing:
        - data: List containing hierarchical structure of departments, managers and employees
        - total_count: Total number of matching records
        - page: Current page number
        - page_size: Records per page
        - total_pages: Total number of pages
    """
    
    # Calucate OFFSET
    offset = (page - 1) * limit
    
    # SQL for total count
    count_sql = """
    WITH RECURSIVE org_tree AS (
        -- Base case (Level 1): Department managers
        SELECT 
            dm.emp_no,
            d.dept_no,
            1 AS level
        FROM dept_manager dm
        JOIN departments d ON dm.dept_no = d.dept_no
        WHERE dm.to_date = '9999-01-01'
            AND (:dept_no IS NULL OR d.dept_no = :dept_no)
        
        UNION ALL
        
        -- Recursive case (Level 2): Employees
        SELECT 
            de.emp_no,
            ot.dept_no,
            ot.level + 1 AS level
        FROM org_tree ot
        JOIN dept_emp de ON ot.dept_no = de.dept_no
        WHERE de.to_date = '9999-01-01'
            AND de.emp_no != ot.emp_no
            AND ot.level = 1
    )
    SELECT COUNT(*) AS total
    FROM org_tree
    """
    
    # Order by birth_date to prioritize employees closest to retirement age (oldest first)
    data_sql = """
    WITH RECURSIVE org_tree AS (
        -- Base case (Level 1): Department managers who have no superiors in this database
        SELECT 
            dm.emp_no,
            e.first_name,
            e.last_name,
            t.title,
            d.dept_no,
            d.dept_name,
            CAST(NULL AS UNSIGNED) AS manager_emp_no,
            CAST('Manager' AS CHAR(20)) AS role_type,
            1 AS level,
            CAST(CONCAT(d.dept_no, '-', dm.emp_no) AS CHAR(500)) AS path
        FROM dept_manager dm
        JOIN departments d ON dm.dept_no = d.dept_no
        JOIN employees e ON dm.emp_no = e.emp_no
        LEFT JOIN titles t ON dm.emp_no = t.emp_no AND t.to_date IS NULL
        WHERE dm.to_date = '9999-01-01'
            AND (:dept_no IS NULL OR d.dept_no = :dept_no)
        
        UNION ALL
        
        -- Recursive case (Level 2): Find subordinates from the previous level (department managers)
        SELECT 
            de.emp_no,
            e.first_name,
            e.last_name,
            t.title,
            ot.dept_no,
            ot.dept_name,
            ot.emp_no AS manager_emp_no,
            CAST('Employee' AS CHAR(20)) AS role_type,
            ot.level + 1 AS level,
            CAST(CONCAT(ot.path, '-', de.emp_no) AS CHAR(500)) AS path
        FROM org_tree ot
        JOIN dept_emp de ON ot.dept_no = de.dept_no
        JOIN employees e ON de.emp_no = e.emp_no
        LEFT JOIN titles t ON de.emp_no = t.emp_no AND t.to_date IS NULL
        WHERE de.to_date = '9999-01-01'
            AND de.emp_no != ot.emp_no
            AND ot.level = 1
            AND ot.path NOT LIKE CONCAT('%', de.emp_no, '%')
    )
    SELECT 
        emp_no,
        first_name,
        last_name,
        title,
        dept_no,
        dept_name,
        manager_emp_no,
        role_type,
        level,
        path
    FROM org_tree
    ORDER BY dept_no, level, emp_no
    LIMIT :limit OFFSET :offset
    """
    
    with engine.connect() as conn:
        # Get total count
        count_result = conn.execute(
            text(count_sql),
            {"dept_no": dept_no}
        )
        total_count = count_result.scalar() or 0
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        # Get data
        data_result = conn.execute(
            text(data_sql),
            {
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