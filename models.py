from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# SQLAlchemy 数据库模型
class User(Base):
    """
    用户数据库模型
    定义用户表的结构和字段
    """
    __tablename__ = "users"
    
    # 主键ID，自增
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    
    # 用户名，唯一且不能为空
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    
    # 邮箱，唯一且不能为空
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    
    # 密码哈希值
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    
    # 真实姓名
    full_name = Column(String(100), nullable=True, comment="真实姓名")
    
    # 用户描述
    description = Column(Text, nullable=True, comment="用户描述")
    
    # 是否激活
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 是否为管理员
    is_admin = Column(Boolean, default=False, comment="是否为管理员")
    
    # 创建时间，自动设置为当前时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 更新时间，自动更新
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# Pydantic 模型用于API请求和响应
class UserBase(BaseModel):
    """
    用户基础模型
    包含用户的基本信息字段
    """
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    """
    创建用户请求模型
    继承基础模型并添加密码字段
    """
    password: str

class UserUpdate(BaseModel):
    """
    更新用户请求模型
    所有字段都是可选的
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """
    用户响应模型
    返回给客户端的用户信息，不包含敏感数据
    """
    id: int
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        # 允许从ORM对象创建Pydantic模型
        from_attributes = True

class UserLogin(BaseModel):
    """
    用户登录请求模型
    """
    username: str
    password: str