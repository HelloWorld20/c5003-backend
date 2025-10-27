from sqlalchemy import text
from .init import engine
from typing import Optional


def db_get_organizational_chart(dept_no: Optional[str] = None, limit: int = 100):
    """
    Build organizational chart using recursive CTE
    
    Parameters:
        dept_no: Department number (None means all departments)
        limit: Limit of returned records (default 100)
    
    Returns:
        List containing hierarchical structure of departments, managers and employees, including manager_emp_no
    """
    
    sql = """
    WITH RECURSIVE org_tree AS (
        -- Base case (Level 1): Department managers who have no superiors in this database
        SELECT 
            dm.emp_no,
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
        title,
        dept_no,
        dept_name,
        manager_emp_no,
        role_type,
        level,
        path
    FROM org_tree
    ORDER BY dept_no, level
    LIMIT :limit
    """
    
    with engine.connect() as conn:
        result = conn.execute(
            text(sql), 
            {"dept_no": dept_no, "limit": limit}
        )
        
        if result.returns_rows:
            rows = result.mappings().all()
            return [dict(row) for row in rows]
        else:
            return []
