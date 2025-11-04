"""
商品相关路由
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.item import Item, ItemCreate, ItemUpdate

router = APIRouter()

# 模拟数据存储（实际应用中应使用数据库）
items_db = []


@router.get("/", response_model=List[Item])
async def get_items(skip: int = 0, limit: int = 100):
    """获取商品列表"""
    return items_db[skip : skip + limit]


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """根据 ID 获取商品"""
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="商品未找到")
    return item


@router.post("/", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    """创建新商品"""
    new_item = {
        "id": len(items_db) + 1,
        **item.model_dump()
    }
    items_db.append(new_item)
    return new_item


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    """更新商品"""
    item_index = next(
        (i for i, item in enumerate(items_db) if item["id"] == item_id),
        None
    )
    if item_index is None:
        raise HTTPException(status_code=404, detail="商品未找到")
    
    update_data = item.model_dump(exclude_unset=True)
    items_db[item_index].update(update_data)
    return items_db[item_index]


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """删除商品"""
    item_index = next(
        (i for i, item in enumerate(items_db) if item["id"] == item_id),
        None
    )
    if item_index is None:
        raise HTTPException(status_code=404, detail="商品未找到")
    
    items_db.pop(item_index)
    return None

