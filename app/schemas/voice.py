"""
语音指令相关Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VoiceCommandRequest(BaseModel):
    """语音指令请求"""
    text: str = Field(..., description="用户输入的文本指令", min_length=1)
    user_id: Optional[str] = Field(None, description="用户ID user_id+session_id 组合唯一标识一个用户")
    department_id: Optional[int] = Field(None, description="部门ID（单位ID）")
    session_id: Optional[str] = Field(None, description="会话ID")
    ai_mode: Optional[str] = Field(None, description="意图识别模式：bge-small-zh 或 deepseek 或者 local")

class VoiceCommandResponse(BaseModel):
    """语音指令响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    menu: Optional[str] = Field(None, description="匹配的菜单名称（单个匹配时）")
    menus: Optional[List[str]] = Field(None, description="匹配的菜单名称列表（多个匹配时）")
    menus_obj: Optional[List[dict]] = Field(None, description="完整菜单对象列表，格式：[{\"type\": \"open_action\", \"actionId\": \"123\", \"timestamp\": \"2025-06-01T12:34:56.789Z\"}]")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    message_data: Optional[dict] = Field(None, description="完整的WebSocket消息对象")


class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""
    type: str = Field(..., description="消息类型")
    menu: Optional[str] = Field(None, description="菜单名称")
    user_id: Optional[str] = Field(None, description="用户ID user_id+session_id 组合唯一标识一个用户")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    data: Optional[dict] = Field(None, description="附加数据")

