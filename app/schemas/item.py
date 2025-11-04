"""
商品相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field
from typing import Optional


class ItemBase(BaseModel):
    """商品基础模式"""
    name: str = Field(..., description="商品名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="商品描述", max_length=500)
    price: float = Field(..., description="商品价格", gt=0)
    quantity: int = Field(..., description="商品数量", ge=0)


class ItemCreate(ItemBase):
    """创建商品的模式"""
    pass


class ItemUpdate(BaseModel):
    """更新商品的模式"""
    name: Optional[str] = Field(None, description="商品名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="商品描述", max_length=500)
    price: Optional[float] = Field(None, description="商品价格", gt=0)
    quantity: Optional[int] = Field(None, description="商品数量", ge=0)


class Item(ItemBase):
    """商品完整模式"""
    id: int = Field(..., description="商品ID")
    
    class Config:
        from_attributes = True

