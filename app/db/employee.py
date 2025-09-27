from sqlalchemy import text
from .init import engine

# def db_get_dept_name():
#     with engine.connect() as conn:
#         result = conn.execute(text('SELECT dept_name FROM departments'))
#         res = []
#         for row in result:
#             print(row[0])
#             res.append(row[0])
#         return res
    
# def db_get_dept():
#     with engine.connect() as conn:
#         result = conn.execute(text('SELECT * FROM departments'))
#         # 将Row对象转换为字典
#         # 遍历result，把每一项（row）传入到for前面的表达式中处理
#         # 等同于js中的result.map(row => dict(row._mapping))
#         res = [dict(row._mapping) for row in result]
#         return res

def db_get_emp_list(pageNo: int, pageSize: int, gender: str, emp_no: int, birth_date: str, hire_date: str, name: str):
    pageNo = pageNo or 1
    pageSize = pageSize or 10
    with engine.connect() as conn:
        sql = f'SELECT * FROM employees'
        if gender:
            sql = sql + f' WHERE gender = \'{gender}\''
        if emp_no:
            sql = sql + f' emp_no = {emp_no}'

        sql = sql + f' LIMIT {pageSize} OFFSET {(pageNo - 1) * pageSize}'

        print('执行sql!!!!!!!!!!!!!!!!!：')
        print(sql)
        result = conn.execute(text(sql))
        print('result结构：：：：：：：：：：：：：：')
        # print(dir(result))
        # print(result.one)
        # print(result.one_or_none)
        # for name in dir(result):
        #     if not name.startswith('_'):
        #         print(name)
        # 判断是否有查询内容返回（SELECT / RETURNING）
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return data
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}