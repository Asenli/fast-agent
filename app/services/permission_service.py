"""
权限验证服务模块
"""
import httpx
from typing import List, Set, Optional
from app.core.config import settings


class PermissionService:
    """权限验证服务"""
    
    @staticmethod
    async def check_menu_permission(user_id: int, menu_name: str, department_id: Optional[int] = None) -> bool:
        """
        检查用户是否有菜单权限
        
        Args:
            user_id: 用户ID
            menu_name: 菜单名称
            department_id: 部门ID（可选）
            
        Returns:
            是否有权限
        """
        # TODO: 替换为实际的权限API
        # 示例：调用外部系统接口
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"http://your-permission-api/permissions/{user_id}",
        #         params={"menu": menu_name, "department_id": department_id}
        #     )
        #     return response.json().get('has_permission', False)
        
        # 临时返回True（开发阶段）- 可根据实际需求修改
        # 实际实现中，应该从load_menus API返回的数据中过滤出有权限的菜单
        return True
    
    @staticmethod
    async def get_user_menus(user_id: str, department_id: Optional[int] = None) -> List[str]:
        """
        获取用户有权限的菜单列表
        
        Args:
            user_id: 用户ID
            department_id: 部门ID（可选）
            
        Returns:
            用户有权限的菜单列表
        """
        # TODO: 替换为实际的权限API
        # 示例：调用外部系统接口
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"http://your-permission-api/permissions/{user_id}/menus",
        #         params={"department_id": department_id}
        #     )
        #     return response.json().get('menus', [])
        
        # 从MenuService获取菜单（load_menus API已经返回了该用户有权限的菜单）
        from app.services.menu_service import MenuService

        return await MenuService.get_all_menus(user_id, department_id)
    
    @staticmethod
    async def filter_menus_by_permission(user_id: str, menu_names: List[str], department_id: Optional[int] = None) -> List[str]:
        """
        过滤菜单列表，只返回用户有权限的菜单
        
        Args:
            user_id: 用户ID
            menu_names: 待过滤的菜单列表
            department_id: 部门ID（可选）
            
        Returns:
            过滤后的菜单列表（用户有权限的）
        """
        # 获取用户有权限的所有菜单
        user_menus = await PermissionService.get_user_menus(user_id, department_id)
        user_menus_set = set(user_menus)
        
        # 过滤出有权限的菜单
        return [menu for menu in menu_names if menu in user_menus_set]

