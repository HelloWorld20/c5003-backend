from sqlalchemy import text
from .init import engine

# 获取列表 
def db_get_emp_list(pageNo: int, pageSize: int, gender: str):
    with engine.connect() as conn:
        # 根据业务需求、传入的参数拼接SQL语句。
        sql = 'SELECT * FROM employees'

        # 将SQL语句传递给数据库。result为数据库的返回
        result = conn.execute(text(sql))

        # 最核心的工作就在于拼接SQL语句。
        # 可能需要多次调用数据库，然后用Python来拼接想要的数据

        # 如果修改数据库的操作，需要提交事务，确保操作生效（获取不需要）
        conn.commit()

        # 下面的代码照抄即可
        if result.returns_rows:
            # 将 Row 对象转成字典，便于 JSON 序列化
            data = result.mappings().all()
            return data
        else:
            # 非查询语句，返回受影响行数
            return {"rowcount": result.rowcount}

# add employee
def db_add_emp():
    pass
# update employee's info
def ab_update_emp():
    pass
# delete one or more employee's record
def db_del_emp():
    pass