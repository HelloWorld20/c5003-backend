from sqlalchemy import text
from .init import engine
from datetime import datetime

def db_title_list(Page_Number: int, Row_Count: int, Employee_ID: int, Title: str, From_Date: str, To_Date: str):
    """
    Query a title list with pagination and optional filtering conditions.
    And use a dictionary mapping to simplify the conditional concatenation logic.
    """
    pageNo = Page_Number or 1
    pageSize = Row_Count or 10
    with engine.connect() as conn:
        sql = 'SELECT * FROM titles'
        
        params = {}
        where_clauses = []

        # 条件字典
        conditions = {
            'Title': Title,
            'Employee_ID': Employee_ID,
            'From_Date': From_Date,
            'To_Date': To_Date
        }

        # 条件映射：字段名 -> SQL 条件模板
        condition_map = {
            'Title': "title = :Title",
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
        params['page_size'] = pageSize
        params['offset'] = (pageNo - 1) * pageSize

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
def db_add_title(Employee_ID: int, Title: str, From_Date: str, To_Date: str = '9999-01-01'):
    """
    Insert a new title record for an employee.
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
        INSERT INTO titles (emp_no, title, from_date, to_date)
        VALUES (:emp_no, :title, :from_date, :to_date)
        """
        
        params = {
            "emp_no": Employee_ID,
            "title": Title,
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
def db_update_title(Employee_ID: int, Title: str, From_Date: str, To_Date: str):
    """
    Update an existing title record's To_Date.
    """
    try:
        # 1. VALIDATE inputs first
        normalized_from_date = normalize_date_string(From_Date)
        normalized_to_date = normalize_date_string(To_Date)

    except ValueError as e:
        return {"rowcount": 0, "status": "error", "message": f"Invalid date format: {e}"}

    with engine.connect() as conn:
        
        sql = """
        UPDATE titles
        SET to_date = :new_to_date
        WHERE emp_no = :emp_no
          AND title = :title
          AND from_date = :from_date
        """
        
        params = {
            "new_to_date": normalized_to_date,
            "emp_no": Employee_ID,
            "title": Title,
            "from_date": normalized_from_date
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
            
# delete one employee's record
def db_del_title(Employee_ID: int, Title: str):
    """
    Delete an employee record from the 'titles' table.
    """
    with engine.connect() as conn:
        
        sql = "DELETE FROM titles WHERE emp_no = :emp_no AND title = :title"
        params = {"emp_no": Employee_ID,
                  "title": Title
        }

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
