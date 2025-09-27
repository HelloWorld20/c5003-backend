from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接配置
DATABASE_URL = "mysql+pymysql://root:Qq742589@localhost:3306/cityu_db?charset=utf8mb4"

# 创建数据库引擎
# echo=True 用于开发环境下查看SQL语句，生产环境建议设为False
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 打印SQL语句，便于调试
    pool_pre_ping=True,  # 连接池预检查，确保连接有效
    pool_recycle=3600,  # 连接回收时间（秒）
    max_overflow=20,  # 连接池溢出大小
    pool_size=10  # 连接池大小
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,  # 不自动提交
    autoflush=False,   # 不自动刷新
    bind=engine        # 绑定到数据库引擎
)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入系统
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"数据库操作错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """
    创建所有数据库表
    在应用启动时调用
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except SQLAlchemyError as e:
        logger.error(f"创建数据库表失败: {e}")
        raise

def drop_tables():
    """
    删除所有数据库表
    谨慎使用，仅用于开发环境重置
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("数据库表删除成功")
    except SQLAlchemyError as e:
        logger.error(f"删除数据库表失败: {e}")
        raise