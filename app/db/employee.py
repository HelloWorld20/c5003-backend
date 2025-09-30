from sqlalchemy import text
from .init import engine



def db_get_emp_list(pageNo: int, pageSize: int, gender: str, emp_no: int, birth_date: str, hire_date: str, name: str):
    """
    根据分页与可选过滤条件查询员工列表。
    使用字典映射简化条件拼接逻辑。
    """
    pageNo = pageNo or 1
    pageSize = pageSize or 10
    with engine.connect() as conn:
        sql = 'SELECT * FROM employees'
        
        # 条件映射：字段名 -> SQL 条件模板
        condition_map = {
            'name': "CONCAT(first_name, ' ', last_name) LIKE '%{value}%'",
            'gender': "gender = '{value}'",
            'emp_no': "emp_no = {value}",
            'birth_date': "birth_date = '{value}'",
            'hire_date': "hire_date = '{value}'"
        }
        
        # 条件字典
        conditions = {
            'name': name,
            'gender': gender,
            'emp_no': emp_no,
            'birth_date': birth_date,
            'hire_date': hire_date
        }
        
        # 生成 WHERE 子句：过滤非空值并格式化
        where_clauses = [
            condition_map[key].format(value=value)
            for key, value in conditions.items()
            if value and key in condition_map
        ]
        
        if where_clauses:
            sql += ' WHERE ' + ' AND '.join(where_clauses)
        
        sql += f' LIMIT {pageSize} OFFSET {(pageNo - 1) * pageSize}'

        print('执行sql：')
        print(sql)
        result = conn.execute(text(sql))
        
        # 判断是否有查询内容返回（SELECT / RETURNING）
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

        sql = 'SELECT * from employees'

        print('执行sql：')
        print(sql)
        result = conn.execute(text(sql))

        # 判断是否有查询内容返回（SELECT / RETURNING）
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return data
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}


# update employee's info
def db_update_emp(emp_no: int, hire_date: str, name: str):
    with engine.connect() as conn:

        sql = 'SELECT * from employees'

        print('执行sql：')
        print(sql)
        result = conn.execute(text(sql))

        # 判断是否有查询内容返回（SELECT / RETURNING）
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return data
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}
            
# delete one or more employee's record
def db_del_emp(emp_no: int):
    with engine.connect() as conn:

        sql = 'SELECT * from employees'

        print('执行sql：')
        print(sql)
        result = conn.execute(text(sql))

        # 判断是否有查询内容返回（SELECT / RETURNING）
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return data
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}