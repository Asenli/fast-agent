"""
API 路由定义
"""
from fastapi import APIRouter
from app.routers import items, users, voice, websocket

# 创建主 API 路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(websocket.router, prefix="", tags=["websocket"])

