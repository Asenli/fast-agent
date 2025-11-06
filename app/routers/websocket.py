"""
WebSocket路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.utils.websocket_manager import manager
import json

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket连接端点
    
    客户端连接后，可以接收菜单导航消息
    当收到消息时，前端应该执行菜单跳转操作
    """
    await manager.connect(websocket, user_id)
    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "message": "WebSocket连接成功"
        })
        
        while True:
            # 接收客户端消息（心跳、确认等）
            data = await websocket.receive_text()
            if data:
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    if message_type == "ping":
                        # 心跳响应
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": message.get("timestamp")
                        })
                    elif message_type == "ack":
                        # 确认收到导航消息
                        menu = message.get("menu")
                        print(f"用户 {user_id} 确认收到菜单导航消息: {menu}")
                except json.JSONDecodeError:
                    # 非JSON消息，忽略
                    pass
                    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"用户 {user_id} 断开WebSocket连接")


@router.get("/ws/status/{user_id}")
async def get_websocket_status(user_id: str):
    """检查WebSocket连接状态"""
    is_connected = manager.is_connected(user_id)
    return {
        "user_id": user_id,
        "connected": is_connected
    }

