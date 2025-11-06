"""
WebSocket连接管理器
"""
from typing import Dict
from fastapi import WebSocket
import json


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 按用户ID管理连接
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        """断开连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        """发送个人消息"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                print(f"发送消息失败: {e}")
                self.disconnect(user_id)
                return False
        return False
    
    async def broadcast(self, message: dict):
        """广播消息"""
        disconnected = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"广播消息失败: {e}")
                disconnected.append(user_id)
        
        for user_id in disconnected:
            self.disconnect(user_id)
    
    def is_connected(self, user_id: str) -> bool:
        """检查用户是否已连接"""
        return user_id in self.active_connections


# 全局连接管理器
manager = ConnectionManager()

