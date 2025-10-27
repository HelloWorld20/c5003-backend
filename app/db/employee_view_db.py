# In app/db/employee_view_db.py

from sqlalchemy import text
from .init import engine

def employee_profile(Page_Number: int, Row_Count: int, Employee_ID: int, Employee_Name: str, Title: str, Salary: int, Department_Number: str, Department: str, Manager_Name: str, Effective_Date: str, End_Date: str):
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
        
        conditions = {
            'Employee_ID': Employee_ID, 'Employee_Name': Employee_Name, 'Title': Title, 'Salary': Salary,
            'Department_Number': Department_Number, 'Department': Department, 'Manager_Name': Manager_Name,
            'Effective_Date': Effective_Date, 'End_Date': End_Date
        }

        condition_map = {
            'Employee_ID': "emp_no = :Employee_ID",
            'Employee_Name': "CONCAT(employee_first_name, ' ', employee_last_name) LIKE :Employee_Name",
            'Title': "title = :Title",
            'Salary': "salary = :Salary",
            'Department_Number': "dept_no = :Department_Number",
            'Department': "dept_name = :Department",
            'Manager_Name': "CONCAT(manager_first_name, ' ', manager_last_name) LIKE :Manager_Name",
            'Effective_Date': "effective_date = :Effective_Date",
            'End_Date': "end_date = :End_Date"
        }

        for key, value in conditions.items():
            if value is not None:
                where_clauses.append(condition_map[key])
                if 'Name' in key:
                    params[key] = f"%{value}%"
                else:
                    params[key] = value
        
        if where_clauses:
            sql += ' WHERE ' + ' AND '.join(where_clauses)

        sql += ' LIMIT :page_size OFFSET :offset'
        params['page_size'] = pageSize
        params['offset'] = (pageNo - 1) * pageSize

        # Execute the query by passing the SQL string and the parameters dictionary
        result = conn.execute(text(sql), params)

        data = result.mappings().all()
        return data
