from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import User, UserCreate, UserUpdate
from passlib.context import CryptContext
from typing import List, Optional
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 明文密码
        
    Returns:
        str: 加密后的密码哈希
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

# 用户CRUD操作
def create_user(db: Session, user: UserCreate) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        user: 用户创建数据
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        SQLAlchemyError: 数据库操作错误
    """
    try:
        # 对密码进行哈希加密
        hashed_password = hash_password(user.password)
        
        # 创建用户对象
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            description=user.description,
            is_active=user.is_active
        )
        
        # 添加到数据库
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"用户创建成功: {user.username}")
        return db_user
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"创建用户失败: {e}")
        raise

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        Optional[User]: 用户对象或None
    """
    try:
        return db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"获取用户失败: {e}")
        raise

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        Optional[User]: 用户对象或None
    """
    try:
        return db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as e:
        logger.error(f"获取用户失败: {e}")
        raise

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    根据邮箱获取用户
    
    Args:
        db: 数据库会话
        email: 邮箱地址
        
    Returns:
        Optional[User]: 用户对象或None
    """
    try:
        return db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"获取用户失败: {e}")
        raise

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    获取用户列表
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 限制返回的记录数
        
    Returns:
        List[User]: 用户列表
    """
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"获取用户列表失败: {e}")
        raise

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    更新用户信息
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        user_update: 更新数据
        
    Returns:
        Optional[User]: 更新后的用户对象或None
        
    Raises:
        SQLAlchemyError: 数据库操作错误
    """
    try:
        # 获取用户
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        # 更新字段
        update_data = user_update.dict(exclude_unset=True)
        
        # 如果包含密码，需要加密
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
        # 应用更新
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"用户更新成功: {db_user.username}")
        return db_user
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"更新用户失败: {e}")
        raise

def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        bool: 是否删除成功
        
    Raises:
        SQLAlchemyError: 数据库操作错误
    """
    try:
        # 获取用户
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        # 删除用户
        db.delete(db_user)
        db.commit()
        
        logger.info(f"用户删除成功: {db_user.username}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"删除用户失败: {e}")
        raise

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    用户身份验证
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        
    Returns:
        Optional[User]: 验证成功返回用户对象，否则返回None
    """
    try:
        user = get_user_by_username(db, username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
        
    except SQLAlchemyError as e:
        logger.error(f"用户认证失败: {e}")
        raise