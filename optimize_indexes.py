#!/usr/bin/env python3
"""
数据库索引优化脚本
用于为employees数据库创建必要的索引以提升查询性能
"""

from sqlalchemy import text
from app.db.init import engine

def create_indexes():
    """
    创建性能优化所需的索引
    """
    index_queries = [
        # dept_emp表索引
        "CREATE INDEX idx_dept_emp_emp_no_from_date ON dept_emp(emp_no, from_date)",
        "CREATE INDEX idx_dept_emp_from_date ON dept_emp(from_date)",
        "CREATE INDEX idx_dept_emp_to_date ON dept_emp(to_date)",
        
        # salaries表索引
        "CREATE INDEX idx_salaries_emp_no_from_date ON salaries(emp_no, from_date)",
        "CREATE INDEX idx_salaries_from_date ON salaries(from_date)",
        "CREATE INDEX idx_salaries_to_date ON salaries(to_date)",
        
        # titles表索引
        "CREATE INDEX idx_titles_emp_no_from_date ON titles(emp_no, from_date)",
        "CREATE INDEX idx_titles_from_date ON titles(from_date)",
        "CREATE INDEX idx_titles_to_date ON titles(to_date)",
        
        # employees表索引
        "CREATE INDEX idx_employees_first_name ON employees(first_name)",
        "CREATE INDEX idx_employees_last_name ON employees(last_name)",
        "CREATE INDEX idx_employees_gender ON employees(gender)",
        "CREATE INDEX idx_employees_birth_date ON employees(birth_date)",
        "CREATE INDEX idx_employees_hire_date ON employees(hire_date)",
        
        # departments表索引
        "CREATE INDEX idx_departments_dept_name ON departments(dept_name)",
    ]
    
    with engine.connect() as conn:
        for query in index_queries:
            try:
                conn.execute(text(query))
                print(f"✓ 成功创建索引: {query}")
            except Exception as e:
                print(f"✗ 创建索引失败 ({query}): {e}")
        conn.commit()

def drop_indexes():
    """
    删除所有创建的索引（用于测试或重置）
    """
    drop_queries = [
        "DROP INDEX idx_dept_emp_emp_no_from_date ON dept_emp",
        "DROP INDEX idx_dept_emp_from_date ON dept_emp",
        "DROP INDEX idx_dept_emp_to_date ON dept_emp",
        
        "DROP INDEX idx_salaries_emp_no_from_date ON salaries",
        "DROP INDEX idx_salaries_from_date ON salaries",
        "DROP INDEX idx_salaries_to_date ON salaries",
        
        "DROP INDEX idx_titles_emp_no_from_date ON titles",
        "DROP INDEX idx_titles_from_date ON titles",
        "DROP INDEX idx_titles_to_date ON titles",
        
        "DROP INDEX idx_employees_first_name ON employees",
        "DROP INDEX idx_employees_last_name ON employees",
        "DROP INDEX idx_employees_gender ON employees",
        "DROP INDEX idx_employees_birth_date ON employees",
        "DROP INDEX idx_employees_hire_date ON employees",
        
        "DROP INDEX idx_departments_dept_name ON departments",
    ]
    
    with engine.connect() as conn:
        for query in drop_queries:
            try:
                conn.execute(text(query))
                print(f"✓ 成功删除索引: {query}")
            except Exception as e:
                print(f"✗ 删除索引失败 ({query}): {e}")
        conn.commit()

if __name__ == "__main__":
    print("开始创建数据库索引...")
    create_indexes()
    print("\n索引创建完成！")
    
    # 如果要删除索引，取消下面的注释
    # print("\n开始删除索引...")
    # drop_indexes()
    # print("索引删除完成！")