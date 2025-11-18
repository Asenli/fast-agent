"""
语音指令路由
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, Union
from datetime import datetime
from app.schemas.voice import VoiceCommandRequest, VoiceCommandResponse
from app.services.menu_service import MenuService
from app.services.ai_service import AIService
from app.services.permission_service import PermissionService
from app.utils.websocket_manager import manager

router = APIRouter()


@router.post("/command", response_model=VoiceCommandResponse)
async def process_voice_command(
    request: VoiceCommandRequest,
    user_id: Optional[Union[str]] = None
):
    """
    处理语音指令
    
    流程：
    1. 接收文本指令，携带用户ID和部门ID
    2. 调用接口获取菜单并构造映射（自动生成分词）
    3. 意图识别匹配菜单（使用动态分词）
    4. 只匹配有权限的菜单
    5. 多个匹配时返回多个，告诉用户再次选择
    6. 单个匹配时推送消息到WebSocket
    """
    try:
        # 获取用户ID和部门ID（优先使用请求中的，否则使用参数或默认值）
        # 确保 user_id 始终是字符串类型
        current_user = str(request.user_id or user_id or "1")
        current_department_id = request.department_id
        
        if not current_user:
            return VoiceCommandResponse(
                success=False,
                message="用户ID不能为空",
                menu=None,
                menus=None
            )
        
        # 1. 调用接口获取菜单列表（带缓存，自动构造映射和生成分词）
        session_id = request.session_id
        menus = await MenuService.get_all_menus(current_user, current_department_id, session_id)
        
        if not menus:
            return VoiceCommandResponse(
                success=False,
                message="系统菜单数据为空，请联系管理员",
                menu=None,
                menus=None
            )
        
        # 2. 获取菜单关键词映射（用于意图识别，实时获取不缓存）
        menu_keywords = await MenuService.build_menu_keywords(menus)
        
        # 3. 调用AI分析匹配菜单（返回多个匹配结果）
        matched_menus = await AIService.match_menus(request.text, menus, menu_keywords, ai_mode=request.ai_mode)
        
        if not matched_menus:
            return VoiceCommandResponse(
                success=False,
                message="小安还在学习中，未理解到您的意思",
                menu=None,
                menus=None
            )
        
        # 4. 过滤出用户有权限的菜单
        authorized_menus = await PermissionService.filter_menus_by_permission(
            current_user, matched_menus, current_department_id
        )
        
        if not authorized_menus:
            return VoiceCommandResponse(
                success=False,
                message="您无操作权限",
                menu=None,
                menus=None
            )
        
        # 5. 处理匹配结果
        if len(authorized_menus) == 1:
            # 单个匹配，直接打开
            matched_menu_name = authorized_menus[0]  # 第三级菜单名称
            # 获取完整路径
            full_path = MenuService.get_full_path_by_menu(matched_menu_name)
            if not full_path:
                full_path = matched_menu_name  # 如果没有找到完整路径，使用原名
            
            # 获取 menu_id
            action_id = MenuService.get_action_id_by_menu(matched_menu_name)
            
            # 推送消息到WebSocket消息中心
            message = {
                # "type": "menu_navigation",
                "type": "open_action",
                "menu": full_path,  # 使用完整路径
                "user_id": current_user,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "type": "open_action",
                    "actionId": action_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # 发送WebSocket消息
            message_sent = await manager.send_personal_message(message, current_user)
            
            if not message_sent:
                # WebSocket未连接，但API调用成功
                return VoiceCommandResponse(
                    success=True,
                    message=f"正在为您打开{full_path}（WebSocket未连接，请刷新页面）",
                    menu=full_path,
                    menus=None,
                    message_data=message
                )
            
            return VoiceCommandResponse(
                success=True,
                message=f"正在为您打开{full_path}",
                menu=full_path,
                menus=None,
                message_data=message
            )
        else:
            # 多个匹配，返回列表让用户选择
            # 将第三级菜单名称转换为完整路径显示
            full_paths = []
            menus_obj = []
            for menu_name in authorized_menus:
                full_path = MenuService.get_full_path_by_menu(menu_name)
                full_paths.append(full_path if full_path else menu_name)
                
                # 获取 action_id
                action_id = MenuService.get_action_id_by_menu(menu_name)
                
                # 从完整路径中提取父级菜单名称（第一级菜单）
                parent_menu_name = None
                if full_path and "-" in full_path:
                    parent_menu_name = full_path.split("-")[0]
                
                # 构造菜单对象
                menu_obj = {
                    "type": "open_action",
                    "actionId": str(action_id) if action_id else None,
                    "timestamp": datetime.now().isoformat(),
                    "name": menu_name,
                    "parentName": parent_menu_name
                }
                menus_obj.append(menu_obj)
            
            menus_text = "、".join(full_paths)
            return VoiceCommandResponse(
                success=True,
                message=f"找到多个匹配的菜单，请选择您要打开的菜单：{menus_text}",
                menu=None,
                menus=full_paths,  # 返回完整路径列表
                menus_obj=menus_obj  # 返回完整菜单对象列表 [{"type": "open_action", "actionId": "123", "timestamp": "2025-06-01T12:34:56.789Z"}]
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理指令失败: {str(e)}")


@router.get("/menus")
async def get_menus():
    """获取所有菜单列表（用于测试）"""
    menus = await MenuService.get_all_menus()
    return {"menus": menus, "count": len(menus)}

