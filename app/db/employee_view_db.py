# In app/db/employee_view_db.py

from sqlalchemy import text
from typing import Optional
from .init import engine

def employee_profile(Page_Number: int, Row_Count: int, Employee_ID_min: Optional[int] = None, Employee_ID_max: Optional[int] = None, 
                    Employee_Name: Optional[str] = None, Title: Optional[str] = None, Salary_min: Optional[int] = None, 
                    Salary_max: Optional[int] = None, Department_Number: Optional[str] = None, Department: Optional[str] = None, 
                    Manager_Name: Optional[str] = None, Effective_Date_min: Optional[str] = None, Effective_Date_max: Optional[str] = None, 
                    End_Date_min: Optional[str] = None, End_Date_max: Optional[str] = None):
    pageNo = Page_Number or 1
    pageSize = Row_Count or 10

    with engine.connect() as conn:
        # Step 1: Create or replace the view.
        # Note: Running this on every API call is inefficient. Consider creating it once when the app starts.
        create_view_sql = """
            CREATE OR REPLACE VIEW employee_profile_history AS
            SELECT
                e.emp_no,
                e.first_name AS employee_first_name,
                e.last_name AS employee_last_name,
                t.title,
                s.salary,
                d.dept_no,
                d.dept_name,
                m.first_name AS manager_first_name,
                m.last_name AS manager_last_name,
                s.from_date AS effective_date,
                s.to_date AS end_date
            FROM
                employees e
            JOIN salaries s ON e.emp_no = s.emp_no
            JOIN titles t ON e.emp_no = t.emp_no AND s.from_date BETWEEN t.from_date AND t.to_date
            JOIN dept_emp de ON e.emp_no = de.emp_no AND s.from_date BETWEEN de.from_date AND de.to_date
            JOIN departments d ON de.dept_no = d.dept_no
            JOIN dept_manager dm ON de.dept_no = dm.dept_no AND s.from_date <= dm.to_date AND dm.from_date <= s.to_date
            JOIN employees m ON dm.emp_no = m.emp_no;
        """
        conn.execute(text(create_view_sql))
        conn.commit()

        # Step 2: Build and execute a safe, parameterized SELECT query.
        sql = "SELECT * FROM employee_profile_history"
        
        params = {}
        where_clauses = []
        
        # Range searches for Employee_ID
        if Employee_ID_min is not None:
            where_clauses.append("emp_no >= :Employee_ID_min")
            params['Employee_ID_min'] = Employee_ID_min
        if Employee_ID_max is not None:
            where_clauses.append("emp_no <= :Employee_ID_max")
            params['Employee_ID_max'] = Employee_ID_max
        
        # Fuzzy search for Employee_Name
        if Employee_Name is not None:
            where_clauses.append("CONCAT(employee_first_name, ' ', employee_last_name) LIKE :Employee_Name")
            params['Employee_Name'] = f"%{Employee_Name}%"
        
        # Fuzzy search for Title
        if Title is not None:
            where_clauses.append("title LIKE :Title")
            params['Title'] = f"%{Title}%"
        
        # Range searches for Salary
        if Salary_min is not None:
            where_clauses.append("salary >= :Salary_min")
            params['Salary_min'] = Salary_min
        if Salary_max is not None:
            where_clauses.append("salary <= :Salary_max")
            params['Salary_max'] = Salary_max
        
        # Exact match for Department_Number
        if Department_Number is not None:
            where_clauses.append("dept_no = :Department_Number")
            params['Department_Number'] = Department_Number
        
        # Fuzzy search for Department
        if Department is not None:
            where_clauses.append("dept_name LIKE :Department")
            params['Department'] = f"%{Department}%"
        
        # Fuzzy search for Manager_Name
        if Manager_Name is not None:
            where_clauses.append("CONCAT(manager_first_name, ' ', manager_last_name) LIKE :Manager_Name")
            params['Manager_Name'] = f"%{Manager_Name}%"
        
        # Range searches for Effective_Date
        if Effective_Date_min is not None:
            where_clauses.append("effective_date >= :Effective_Date_min")
            params['Effective_Date_min'] = Effective_Date_min
        if Effective_Date_max is not None:
            where_clauses.append("effective_date <= :Effective_Date_max")
            params['Effective_Date_max'] = Effective_Date_max
        
        # Range searches for End_Date
        if End_Date_min is not None:
            where_clauses.append("end_date >= :End_Date_min")
            params['End_Date_min'] = End_Date_min
        if End_Date_max is not None:
            where_clauses.append("end_date <= :End_Date_max")
            params['End_Date_max'] = End_Date_max
        
        if where_clauses:
            sql += ' WHERE ' + ' AND '.join(where_clauses)

        sql += ' LIMIT :page_size OFFSET :offset'
        params['page_size'] = pageSize
        params['offset'] = (pageNo - 1) * pageSize

        # Execute the query by passing the SQL string and the parameters dictionary
        result = conn.execute(text(sql), params)

        data = result.mappings().all()
        return data
