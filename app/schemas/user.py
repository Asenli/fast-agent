"""
用户相关的 Pydantic 模式
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., description="用户名", min_length=3, max_length=50)


class UserCreate(UserBase):
    """创建用户的模式"""
    password: str = Field(..., description="密码", min_length=6)


class UserUpdate(BaseModel):
    """更新用户的模式"""
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    username: Optional[str] = Field(None, description="用户名", min_length=3, max_length=50)
    password: Optional[str] = Field(None, description="密码", min_length=6)


class User(UserBase):
    """用户完整模式"""
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        from_attributes = True

