from sqlalchemy import text
from .init import engine
from datetime import datetime

def db_dept_list(Page_Number: int, Row_Count: int, Dept_ID: str, Dept_Name: str):
    """
    Query a department list with pagination and optional filtering conditions.
    And use a dictionary mapping to simplify the conditional concatenation logic.
    """
    pageNo = Page_Number or 1
    pageSize = Row_Count or 10
    with engine.connect() as conn:
        sql = 'SELECT * FROM departments'
        
        params = {}
        where_clauses = []

        # 条件字典
        conditions = {
            'Dept_Name': Dept_Name,
            'Dept_ID': Dept_ID,
        }

        # 条件映射：字段名 -> SQL 条件模板
        condition_map = {
            'Dept_Name': "dept_name = :Dept_Name",
            'Dept_ID': "dept_no = :Dept_ID",
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

# add dept
def db_add_dept(Dept_ID: str, Dept_Name: str):
    """
    Insert a new department.
    """

    with engine.connect() as conn:
        
        sql = """
        INSERT INTO departments (dept_no, dept_name)
        VALUES (:dept_no, :dept_name)
        """
        
        params = {
            "dept_no": Dept_ID,
            "dept_name": Dept_Name,
        }

        try:
            # 2. EXECUTE database logic inside its own try block
            result = conn.execute(text(sql), params)
            conn.commit()
            return {"rowcount": result.rowcount, "status": "success"}
        
        except Exception as e:
            # 3. ROLLBACK on error
            conn.rollback()
            return {"rowcount": 0, "status": "error", "message": str(e)}


# update dept's info
def db_update_dept(Dept_ID: str, Dept_Name: str):
    """
    Update an existing department record.
    """

    with engine.connect() as conn:
        
        sql = """
        UPDATE departments
        SET dept_name = :new_dept_name
        WHERE dept_no = :dept_no
        """
        
        params = {
            "new_dept_name": Dept_Name,
            "dept_no": Dept_ID,
        }

        try:
            # 2. EXECUTE database logic
            result = conn.execute(text(sql), params)
            conn.commit()
            
            if result.rowcount > 0:
                return {"rowcount": result.rowcount, "status": "success"}
            else:
                return {"rowcount": 0, "status": "not_found", "message": "No matching title record found to update."}
        
        except Exception as e:
            # 3. ROLLBACK on error
            conn.rollback()
            return {"rowcount": 0, "status": "error", "message": str(e)}
            
# delete one dept's record
def db_del_dept(Dept_ID: str, Dept_Name: str):
    """
    Delete an department record from the 'departments' table.
    """
    with engine.connect() as conn:
        
        sql = "DELETE FROM departments WHERE dept_no = :dept_no AND dept_name = :dept_name"
        params = {"dept_no": Dept_ID,
                  "dept_name": Dept_Name}

        try:
            # 1. EXECUTE database logic
            result = conn.execute(text(sql), params)
            conn.commit()

            if result.rowcount > 0:
                return {"rowcount": result.rowcount, "status": "success"}
            else:
                return {"rowcount": 0, "status": "not_found", "message": "No employee found with that emp_no to delete."}
        
        except Exception as e:
            # 2. ROLLBACK on error (e.g., Foreign Key violation)
            conn.rollback()
            return {"rowcount": 0, "status": "error", "message": str(e)}
