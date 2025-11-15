from sqlalchemy import text
from .init import engine
from datetime import datetime

def db_dept_manager_list(Page_Number: int, Row_Count: int, Employee_ID: int, Dept_Number: str, From_Date: str, To_Date: str):
    """
    Query a department manager list with pagination and optional filtering conditions.
    Only shows current managers (where MAX(to_date) = '9999-01-01').
    And use a dictionary mapping to simplify the conditional concatenation logic.
    """
    Page_Number = Page_Number or 1
    Row_Count = Row_Count or 10
    with engine.connect() as conn:
        # Only show current managers: filter where MAX(to_date) = '9999-01-01'
        sql = """
        SELECT dm.* FROM dept_manager dm
        WHERE (
            SELECT MAX(dm_check.to_date)
            FROM dept_manager dm_check
            WHERE dm_check.emp_no = dm.emp_no
              AND dm_check.dept_no = dm.dept_no
        ) = '9999-01-01'
        """
        
        params = {}
        where_clauses = []

        # 条件字典
        conditions = {
            'Dept_Number': Dept_Number,
            'Employee_ID': Employee_ID,
            'From_Date': From_Date,
            'To_Date': To_Date
        }

        # 条件映射：字段名 -> SQL 条件模板
        condition_map = {
            'Dept_Number': "dm.dept_no = :Dept_Number",
            'Employee_ID': "dm.emp_no = :Employee_ID",
            'From_Date': "dm.from_date = :From_Date",
            'To_Date': "dm.to_date = :To_Date"
        }
        
        for key, value in conditions.items():
            if value is not None:
                where_clauses.append(condition_map[key])
                if 'Name' in key:
                    params[key] = f"%{value}%"
                else:
                    params[key] = value
        
        if where_clauses:
            sql += ' AND ' + ' AND '.join(where_clauses)

        sql += ' LIMIT :page_size OFFSET :offset'
        params['page_size'] = Row_Count
        params['offset'] = (Page_Number - 1) * Row_Count

        # Execute the query by passing the SQL string and the parameters dictionary
        result = conn.execute(text(sql), params)

        data = result.mappings().all()
        return data

def db_dept_manager_list_all(Page_Number: int, Row_Count: int, Employee_ID: int, Dept_Number: str, From_Date: str, To_Date: str):
    """
    Query all department manager records (including historical) with pagination and optional filtering conditions.
    This is for viewing all managers, not just current ones.
    """
    Page_Number = Page_Number or 1
    Row_Count = Row_Count or 10
    with engine.connect() as conn:
        sql = 'SELECT * FROM dept_manager'
        
        params = {}
        where_clauses = []

        # 条件字典
        conditions = {
            'Dept_Number': Dept_Number,
            'Employee_ID': Employee_ID,
            'From_Date': From_Date,
            'To_Date': To_Date
        }

        # 条件映射：字段名 -> SQL 条件模板
        condition_map = {
            'Dept_Number': "dept_no = :Dept_Number",
            'Employee_ID': "emp_no = :Employee_ID",
            'From_Date': "from_date = :From_Date",
            'To_Date': "to_date = :To_Date"
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
        params['page_size'] = Row_Count
        params['offset'] = (Page_Number - 1) * Row_Count

        # Execute the query by passing the SQL string and the parameters dictionary
        result = conn.execute(text(sql), params)

        data = result.mappings().all()
        return data

def normalize_date_string(date_string: str) -> str:
    """
    Tries to parse a date or timestamp string from common formats.
    Returns the date part as a 'YYYY-MM-DD' string.
    Raises ValueError if the format is not recognized or input is invalid.
    """
    if not isinstance(date_string, str):
        raise ValueError(f"Input must be a string, not {type(date_string)}")

    # List of formats to try (timestamps included)
    common_formats = [
        # Date only
        '%Y-%m-%d',     
        '%d-%m-%Y',     
        '%m/%d/%Y',     
        '%d/%m/%Y',     
        
        # Date and Time (Timestamp)
        '%Y-%m-%d %H:%M:%S',
        '%d-%m-%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S', # ISO 8601 Timestamp
    ]
    
    for fmt in common_formats:
        try:
            dt_obj = datetime.strptime(date_string, fmt)
            return dt_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue

    raise ValueError(f"Date/Time '{date_string}' is not in a recognized format.")

# add title
def db_add_dept_manager(Employee_ID: int, Dept_Number: str, From_Date: str, To_Date: str = '9999-01-01'):
    """
    Insert a new record for a department manager.
    """
    try:
        # 1. VALIDATE inputs first
        normalized_from_date = normalize_date_string(From_Date)
        normalized_to_date = normalize_date_string(To_Date)

    except ValueError as e:
        # Return a clean error if validation fails
        return {"rowcount": 0, "status": "error", "message": f"Invalid date format: {e}"}

    with engine.connect() as conn:
        
        sql = """
        INSERT INTO dept_manager (emp_no, dept_no, from_date, to_date)
        VALUES (:emp_no, :dept_no, :from_date, :to_date)
        """
        
        params = {
            "emp_no": Employee_ID,
            "dept_no": Dept_Number,
            "from_date": normalized_from_date,
            "to_date": normalized_to_date
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


# update employee's info
def db_update_dept_manager(Employee_ID: int, Dept_Number: str, From_Date: str, To_Date: str):
    """
    Update an existing department manager record's To_Date.
    """
    try:
        # 1. VALIDATE inputs first
        normalized_from_date = normalize_date_string(From_Date)
        normalized_to_date = normalize_date_string(To_Date)

    except ValueError as e:
        return {"rowcount": 0, "status": "error", "message": f"Invalid date format: {e}"}

    with engine.connect() as conn:
        
        sql = """
        UPDATE dept_manager
        SET to_date = :new_to_date
        WHERE emp_no = :emp_no
          AND dept_no = :dept_no
          AND from_date = :from_date
        """
        
        params = {
            "new_to_date": normalized_to_date,
            "emp_no": Employee_ID,
            "dept_no": Dept_Number,
            "from_date": normalized_from_date
        }

        try:
            # 2. EXECUTE database logic
            result = conn.execute(text(sql), params)
            conn.commit()
            
            if result.rowcount > 0:
                return {"rowcount": result.rowcount, "status": "success"}
            else:
                return {"rowcount": 0, "status": "not_found", "message": "No matching department employee record found to update."}
        
        except Exception as e:
            # 3. ROLLBACK on error
            conn.rollback()
            return {"rowcount": 0, "status": "error", "message": str(e)}
            
# delete one employee's record
def db_del_dept_manager(Employee_ID: int, Dept_Number: str):
    """
    Delete an employee record from the 'dept_manager' table.
    """
    with engine.connect() as conn:
        
        sql = "DELETE FROM dept_manager WHERE emp_no = :emp_no AND dept_no = :dept_no"
        params = {"emp_no": Employee_ID,
                  "dept_no": Dept_Number
        }

        try:
            # 1. EXECUTE database logic
            result = conn.execute(text(sql), params)
            conn.commit()

            if result.rowcount > 0:
                return {"rowcount": result.rowcount, "status": "success"}
            else:
                return {"rowcount": 0, "status": "not_found", "message": "No department employee found with that emp_no to delete."}
        
        except Exception as e:
            # 2. ROLLBACK on error (e.g., Foreign Key violation)
            conn.rollback()
            return {"rowcount": 0, "status": "error", "message": str(e)}
