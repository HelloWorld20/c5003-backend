from sqlalchemy import text, create_engine

db_user = 'root'
db_password = 'Qq742589'
db_name = 'employees'
host = 'localhost'
port = '3306'

# 数据库连接配置
DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{host}:{port}/{db_name}?charset=utf8mb4"


engine = create_engine(
        DATABASE_URL,
        echo=True,  # 打印SQL语句，便于调试
        pool_pre_ping=True,  # 连接池预检查，确保连接有效
        pool_recycle=3600,  # 连接回收时间（秒）
        max_overflow=20,  # 连接池溢出大小
        pool_size=10  # 连接池大小
    )