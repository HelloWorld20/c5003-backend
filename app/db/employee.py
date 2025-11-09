from sqlalchemy import text
from .init import engine
import random
from datetime import datetime



def format_timestamp_to_date(timestamp_str):
    """
    将时间戳字符串转换为SQL date格式 (YYYY-MM-DD)
    支持多种时间戳格式：
    - Unix时间戳（秒或毫秒）
    - ISO 8601格式字符串
    - 其他常见日期时间格式
    """
    try:
        # 如果是Unix时间戳（数字字符串）
        if timestamp_str.isdigit():
            timestamp = int(timestamp_str)
            # 判断是秒还是毫秒
            if timestamp > 10000000000:  # 毫秒时间戳（大于10^10）
                timestamp = timestamp / 1000
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        else:
            # 尝试解析ISO 8601或其他日期格式
            # 尝试多种日期格式
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S', 
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%m/%d/%Y'
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            # 如果所有格式都失败，返回原始字符串
            return timestamp_str
    except (ValueError, AttributeError):
        # 如果转换失败，返回原始字符串
        return timestamp_str

def db_get_emp_list(page: int, pageSize: int, gender: str, emp_no: int, birth_date_start: str, birth_date_end: str,  hire_date_start: str, hire_date_end: str,  name: str):
    """
    Query an employee list with pagination and optional filtering conditions.
    And use a dictionary mapping to simplify the conditional concatenation logic.
    """
    page = page or 1
    pageSize = pageSize or 10
    with engine.connect() as conn:
        sql = """
            SELECT * FROM employees E
            JOIN dept_emp DE ON E.emp_no = DE.emp_no
            JOIN departments d ON d.dept_no = DE.dept_no
            JOIN titles T ON T.emp_no = E.emp_no AND T.from_date = (SELECT MAX(from_date) FROM titles WHERE emp_no = E.emp_no)
            JOIN salaries S ON S.emp_no = E.emp_no AND S.from_date = (SELECT MAX(from_date) FROM salaries WHERE emp_no = E.emp_no)
        """
        
        # 条件映射：字段名 -> SQL 条件模板
        condition_map = {
            'name': "CONCAT(first_name, ' ', last_name) LIKE '%{value}%'",
            'gender': "gender = '{value}'",
            'emp_no': "emp_no = {value}",
        }
        
        # 条件字典
        conditions = {
            'name': name,
            'gender': gender,
            'emp_no': emp_no,
        }
        
        # 生成 WHERE 子句：过滤非空值并格式化
        where_clauses = [
            condition_map[key].format(value=value)
            for key, value in conditions.items()
            if value and key in condition_map
        ]
        
        # 处理日期范围条件
        if birth_date_start and birth_date_end:
            where_clauses.append(f"birth_date BETWEEN '{birth_date_start}' AND '{birth_date_end}'")
        elif birth_date_start:
            where_clauses.append(f"birth_date >= '{birth_date_start}'")
        elif birth_date_end:
            where_clauses.append(f"birth_date <= '{birth_date_end}'")
            
        if hire_date_start and hire_date_end:
            where_clauses.append(f"hire_date BETWEEN '{hire_date_start}' AND '{hire_date_end}'")
        elif hire_date_start:
            where_clauses.append(f"hire_date >= '{hire_date_start}'")
        elif hire_date_end:
            where_clauses.append(f"hire_date <= '{hire_date_end}'")
        
        if where_clauses:
            sql += ' WHERE ' + ' AND '.join(where_clauses)
            # countSql += ' WHERE ' + ' AND '.join(where_clauses)

        
        sql += f' LIMIT {pageSize} OFFSET {(page - 1) * pageSize}'

        print('Execute SQL：')
        print(sql)
        # print(countSql)
        result = conn.execute(text(sql))
       

        # countResult = conn.execute(text(countSql))
        # print(dir(result))
        # print('我想看的值：')
        # 读取 count(*) 的值：fetchone() 返回一个 Row，再取下标 0
        # total = countResult.fetchone()[0]
        # print("Record Count：", total)
        # 判断是否有查询内容返回（SELECT / RETURNING）
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return {'data': data, 'total': -1}
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}

# get employee info by emp_no
def get_emp_info(emp_no: int):
    with engine.connect() as conn:
        sql = f"""
            SELECT * FROM employees E
            JOIN dept_emp DE ON E.emp_no = DE.emp_no
            JOIN departments D ON DE.dept_no = D.dept_no
            JOIN titles T ON E.emp_no = T.emp_no AND T.from_date = (SELECT MAX(from_date) FROM titles WHERE emp_no = E.emp_no)
            JOIN salaries S ON E.emp_no = S.emp_no AND S.from_date = (SELECT MAX(from_date) FROM salaries WHERE emp_no = E.emp_no)
            WHERE E.emp_no = {emp_no}
        """

        print('Execute SQL：')
        print(sql)
        result = conn.execute(text(sql))
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return data
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}


# add employee
def db_add_emp(gender: str, birth_date: str, hire_date: str, name: str):
    with engine.connect() as conn:
        emp_no = int(random.random() * 1000000000)

        parts = name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        hire_date = format_timestamp_to_date(hire_date)
        birth_date = format_timestamp_to_date(birth_date)

        sql = f'INSERT INTO employees (emp_no, birth_date, first_name, last_name, gender, hire_date) VALUES ({emp_no}, \'{birth_date}\', \'{first_name}\', \'{last_name}\', \'{gender}\', \'{hire_date}\')'
        # INSERT INTO table_name (column1, column2, column3, ...)
        # VALUES (value1, value2, value3, ...)

        print('Execute SQL：')
        print(sql)
        result = conn.execute(text(sql))
        
        # 提交事务，确保操作生效
        conn.commit()
        # 判断是否有查询内容返回（SELECT / RETURNING）
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return data
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}


# update employee's info
def db_update_emp(emp_no: str, gender: str, birth_date: str, hire_date: str, name: str, 
                  dept_no: str = None, title: str = None, salary: int = None, 
                  from_date: str = None, to_date: str = None):
    """
    更新员工信息，支持多表更新（employees, dept_emp, titles, salaries）
    
    参数:
    - emp_no: 员工编号（必需）
    - gender, birth_date, hire_date, name: 员工基本信息
    - dept_no: 部门编号（更新部门关系）
    - title: 职称（更新职称）
    - salary: 薪资（更新薪资）
    - from_date: 开始日期（用于部门关系、职称、薪资）
    - to_date: 结束日期（用于部门关系、职称、薪资）
    """
    with engine.begin() as conn:  # 使用事务，自动提交或回滚
        
        # 1. 更新 employees 表
        update_operations = []
        
        parts = name.split(' ', 1) if name else ('', '')
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        conditions = {}

        if gender:
            conditions['gender'] = gender
        if name:
            conditions['first_name'] = first_name
            conditions['last_name'] = last_name
        if birth_date:
            conditions['birth_date'] = birth_date
        if hire_date:
            conditions['hire_date'] = hire_date

        if conditions:
            set_map = {
                'gender': "gender = '{value}'",
                'birth_date': "birth_date = '{value}'",
                'hire_date': "hire_date = '{value}'",
                'first_name': "first_name = '{value}'",
                'last_name': "last_name = '{value}'"
            }

            set_clauses = [
                set_map[key].format(value=value)
                for key, value in conditions.items()
                if value and key in set_map
            ]
            
            if set_clauses:
                sql = f'UPDATE employees SET {", ".join(set_clauses)} WHERE emp_no = {emp_no}'
                update_operations.append(sql)

        # 2. 更新 dept_emp 表（部门关系）
        print('dept_nodept_nodept_nodept_nodept_no update', dept_no)

        if dept_no:
            
            # 先结束当前部门关系
            end_current_dept_sql = f"""
                UPDATE dept_emp 
                SET to_date = '{from_date or '9999-01-01'}' 
                WHERE emp_no = {emp_no} AND to_date = '9999-01-01'
            """
            update_operations.append(end_current_dept_sql)
            
            # 添加新的部门关系
            new_dept_sql = f"""
                INSERT INTO dept_emp (emp_no, dept_no, from_date, to_date)
                VALUES ({emp_no}, '{dept_no}', '{from_date or '9999-01-01'}', '{to_date or '9999-01-01'}')
            """
            update_operations.append(new_dept_sql)

        # 3. 更新 titles 表（职称）
        if title:
            # 先结束当前职称
            end_current_title_sql = f"""
                UPDATE titles 
                SET to_date = '{from_date or '9999-01-01'}' 
                WHERE emp_no = {emp_no} AND to_date = '9999-01-01'
            """
            update_operations.append(end_current_title_sql)
            
            # 添加新的职称
            new_title_sql = f"""
                INSERT INTO titles (emp_no, title, from_date, to_date)
                VALUES ({emp_no}, '{title}', '{from_date or '9999-01-01'}', '{to_date or '9999-01-01'}')
            """
            update_operations.append(new_title_sql)

        # 4. 更新 salaries 表（薪资）
        if salary is not None:
            # 先结束当前薪资
            end_current_salary_sql = f"""
                UPDATE salaries 
                SET to_date = '{from_date or '9999-01-01'}' 
                WHERE emp_no = {emp_no} AND to_date = '9999-01-01'
            """
            update_operations.append(end_current_salary_sql)
            
            # 添加新的薪资
            new_salary_sql = f"""
                INSERT INTO salaries (emp_no, salary, from_date, to_date)
                VALUES ({emp_no}, {salary}, '{from_date or '9999-01-01'}', '{to_date or '9999-01-01'}')
            """
            update_operations.append(new_salary_sql)

        # 执行所有更新操作
        total_affected = 0
        for sql in update_operations:
            print('Execute SQL：')
            print(sql)
            result = conn.execute(text(sql))
            total_affected += result.rowcount

        return {"rowcount": total_affected, "operations": len(update_operations)}
            
# delete one or more employee's record
def db_del_emp(emp_no: int):
    with engine.connect() as conn:

        sql = f'DELETE from employees WHERE emp_no = {emp_no}'

        print('Execute SQL Deletion：')
        print(sql)
        result = conn.execute(text(sql))
        
        # 提交事务，确保删除操作生效
        conn.commit()

        # 返回受影响的行数
        return {"rowcount": result.rowcount}
