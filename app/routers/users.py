"""
用户相关路由
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()

# 模拟数据存储（实际应用中应使用数据库）
users_db = []


@router.get("/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100):
    """获取用户列表"""
    return users_db[skip : skip + limit]


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """根据 ID 获取用户"""
    user = next((user for user in users_db if user["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user


@router.post("/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """创建新用户"""
    new_user = {
        "id": len(users_db) + 1,
        **user.model_dump()
    }
    users_db.append(new_user)
    return new_user


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    """更新用户"""
    user_index = next(
        (i for i, user in enumerate(users_db) if user["id"] == user_id),
        None
    )
    if user_index is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    update_data = user.model_dump(exclude_unset=True)
    users_db[user_index].update(update_data)
    return users_db[user_index]


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """删除用户"""
    user_index = next(
        (i for i, user in enumerate(users_db) if user["id"] == user_id),
        None
    )
    if user_index is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    users_db.pop(user_index)
    return None

