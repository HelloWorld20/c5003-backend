from sqlalchemy import text
from .init import engine
# import json

import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def executor(sql: str):
    """
    执行SQL查询语句
    
    Args:
        sql (str): 要执行的SQL查询语句
        
    Returns:
        list: 查询结果列表
        
    Raises:
        ValueError: 当SQL语句为空时抛出
        Exception: 将数据库执行过程中的所有异常向上抛出
    """
    if not sql:
        raise ValueError("SQL query cannot be empty")
    
    try:
        with engine.begin() as conn:
            logger.info('最终执行语句')
            logger.info(sql)
            result = conn.execute(text(sql))
            # 判断是否有查询内容返回（SELECT / RETURNING）
            if result.returns_rows:
                # 将 Row 对象转成字典，便于 JSON 序列化
                data = result.mappings().all()
                return data
            else:
                # 非查询语句，返回受影响行数
                return {"rowcount": result.rowcount}
                
    except Exception as e:
        # 记录错误日志
        logger.error(f"SQL执行失败: {sql}")
        logger.error(f"错误信息: {str(e)}")
        # 将数据库异常向上抛出
        raise e