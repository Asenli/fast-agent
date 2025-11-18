"""
菜单服务模块
"""
from typing import List, Dict, Any, Optional, Set
import json
import logging
import re
from datetime import datetime
import httpx
from app.core.config import settings


logger = logging.getLogger(__name__)


class MenuService:
    """菜单服务 - 支持缓存和API查询"""
    
    _cache: dict = {}  # 格式: {f"{user_id}_{department_id}": {"menus": [...], "time": datetime}}
    _cache_time: datetime = None
    # 第三级菜单名称 -> menu_id 的映射
    _menu_to_action_id: Dict[str, int] = {
        # # 根据截图临时映射，后续可补充/修正
        # "中心温度查验": 1548,
        # "食材成本差异": 1544,
        # "膳食全景大屏": 1540,
        # "预案大屏": 1537,
        # "营养膳食": 1533,
        # "营养配餐": 1532,
        # # 1531 名称截图不清晰，暂不写入
        # "巡检结果分析": 1515,
        # "巡检任务统计": 1514,
        # "试运营样品记录(旧)": 1513,
        # "每日菜单(旧)": 1512,
        # "巡检记录": 1511,
        # # 1510/1509 截图不清晰，暂略
        # "巡检计划": 1507,
        # "巡检清单": 1506,
        # "巡检项目库": 1505,
        # "巡检分析": 1504,
        # "巡检任务": 1503,
        # "巡检配置": 1502,
        # "食安巡检": 1501,
        # "营养膳食咨询": 1444,
        # "提问咨询": 1443,
        # "就餐提醒记录": 1442,
        # "伙食费入口表": 1441,
        # # 1440 名称不清晰，暂略
        # "加工制作": 1439,
        # "物业服务": 1437,
        # "售后": 1436,
        # "家长端": 1435,
        # "膳食营养评测规则": 1434,
        # "学校营养膳食分析表": 1433,
        # "膳食营养数据分析": 1432,
        # "评分规则": 1431,
        # "智慧营养数据大屏": 1429,
        # # 1428/1427 名称不清晰，暂略
        # "食安菜谱": 1426,
        # "财务管理": 1154,
        # # 1425/1424 名称不清晰，暂略
    }
    # 第三级菜单名称 -> 完整路径 的映射（用于显示，格式：第一级-第三级）
    _menu_to_full_path: Dict[str, str] = {}
    
    @classmethod
    async def get_all_menus(cls, user_id: Optional[str] = None, department_id: Optional[int] = None, session_id: Optional[str] = None) -> List[str]:
        """
        获取所有菜单列表（带缓存）。
        
        注意：每次调用都会重新从API获取菜单并更新 _menu_to_action_id 映射，
        确保映射数据始终保持最新，避免因连接断开导致映射丢失的问题。

        参数：
        - user_id: 用户ID（用于按用户维度缓存与拉取有权限菜单）
        - department_id: 部门ID/单位ID（参与缓存键与权限范围计算）
        - session_id: 会话ID（透传给下游接口，当前未使用）

        返回：
        - 第三级菜单中文名称列表（用于意图匹配与权限过滤）；映射信息存于类字段。
        """
        # 每次调用都重新从API获取菜单，确保 _menu_to_action_id 映射始终最新
        menus = await cls._fetch_menus_from_api(user_id, department_id, session_id)
        
        # 更新缓存（用于其他可能的用途）
        if menus:
            cache_key = f"{user_id or 'default'}_{department_id or 'default'}"
            cls._cache[cache_key] = {
                'menus': menus,
                'time': datetime.now()
            }
        
        return menus
    
    @classmethod
    async def _fetch_menus_from_api(cls, user_id: Optional[int] = None, department_id: Optional[int] = None, session_id: Optional[str] = None) -> List[str]:
        """
        从外部菜单 API 获取菜单树并更新映射（第三级中文名 -> menu_id 以及 完整路径）。

        参数：
        - user_id/department_id: 覆盖默认配置，用于按用户/单位拉取有权限的菜单
        - session_id: 会话标识（预留参数）

        请求：
        - URL: `{MENU_API_BASE_URL}/api/v1/menu/load_menus`
        - Method: POST，JSON 体包含 user_id/department_id/httpWithoutRpc
        - Headers/Cookies: 支持自定义 Cookie（如需要登录态）

        响应期望结构（示例）：
        - dataList: 三级结构，叶子包含 `title` 与 `action`（menu_id）
        - 兼容 data / children 等旧结构

        行为：
        - 解析三级结构，保存：
          1) `_menu_to_action_id[第三级中文名] = menu_id`
          2) `_menu_to_full_path[第三级中文名] = "第一级-第三级"`
        - 可配合 `build_menu_keywords` 实时生成菜单关键词以支持意图匹配
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 构建请求URL
                url = f"{settings.MENU_API_BASE_URL}/api/v1/menu/load_menus"
                user_id_split_list = user_id.split("_") if user_id else []
                user_id = int(user_id_split_list[0]) if user_id and len(user_id_split_list) > 0 else 0
                # 构建请求体 - 优先使用传入的参数，否则使用配置中的值
                payload = {
                    # "session_id": session_id,
                    "department_id": department_id,
                    "user_id": user_id,
                    "httpWithoutRpc": True
                }
                
                # 构建请求头
                headers = {
                    "Accept": "*/*",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Origin": settings.MENU_API_BASE_URL,
                    "Pragma": "no-cache",
                    # "Referer": f"{settings.MENU_API_BASE_URL}/jicai/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
                }
                
                # 添加 Cookie（如果配置了）
                cookies = {}
                if settings.MENU_API_COOKIE:
                    # 解析 Cookie 字符串
                    for cookie_pair in settings.MENU_API_COOKIE.split(';'):
                        if '=' in cookie_pair:
                            key, value = cookie_pair.strip().split('=', 1)
                            cookies[key] = value
                
                logger.info(
                    "调用菜单API url=%s payload=%s headers=%s cookies_keys=%s",
                    url,
                    payload,
                    {k: headers.get(k) for k in ("Content-Type", "User-Agent", "Origin")},
                    list(cookies.keys()),
                )

                # 发送POST请求
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    cookies=cookies
                )
                response.raise_for_status()
                
                data = response.json()
                
                # 从响应中提取菜单树并更新映射
                # API响应结构：{ "returnCode": 0, "returnMessage": "success", "dataList": [...] }
                if isinstance(data, dict):
                    # 从 dataList 中提取菜单树
                    data_list = data.get("dataList")
                    if isinstance(data_list, list):
                        # 解析三级菜单结构，构建完整路径
                        cls._parse_data_list_menu_structure(data_list)
                    else:
                        # 兼容旧格式：尝试从 data 字段获取菜单树
                        menu_tree = data.get("data") or data.get("children") or data
                        if isinstance(menu_tree, dict):
                            if "children" in menu_tree:
                                cls.update_menu_mapping_from_children(menu_tree["children"])
                            else:
                                cls.reset_menu_mapping_from_tree(menu_tree)
                        elif isinstance(menu_tree, list):
                            cls.update_menu_mapping_from_children(menu_tree)
                
                # 从更新后的映射中提取菜单名称列表
                menu_names = list(cls._menu_to_action_id.keys())
                
                # 更新菜单分词缓存（本地+外部增强）
                return menu_names if menu_names else []
                
        except Exception as e:
            # 如果API调用失败，记录错误并返回默认菜单列表
            logger.error(f"从API获取菜单失败: {str(e)}")
            # 返回默认菜单列表（保留原有硬编码的映射）
            menu_names = list(cls._menu_to_action_id.keys()) if cls._menu_to_action_id else []
            # 更新菜单分词缓存
            if menu_names:
                cls._generate_menu_keywords(menu_names)
            return menu_names
    
    @classmethod
    def clear_cache(cls):
        """清除缓存"""
        cls._cache = {}
        cls._cache_time = None
    
    @classmethod
    async def _fetch_external_menu_keywords(cls, menus: List[str]) -> Dict[str, List[str]]:
        """
        从外部接口批量获取菜单关键词，接口：
        {MENU_API_BASE_URL}/api/v1/menu/cache_menus_keys

        请求体：{"menus": ["菜单1", "菜单2", ...]}
        期望响应：{"code":0, "msg":"ok", "data": [ {"菜单1": ["kw1","kw2"]}, {"菜单2": ["kw1"]} ]}
        返回统一结构：{menu_name: [keywords...]}
        """
        if not menus:
            return {}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{settings.MENU_API_BASE_URL}/api/v1/menu/cache_menus_keys"
                payload = {"menus": menus}
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "fast-agent/menus"
                }
                cookies = {}
                if settings.MENU_API_COOKIE:
                    for cookie_pair in settings.MENU_API_COOKIE.split(';'):
                        if '=' in cookie_pair:
                            key, value = cookie_pair.strip().split('=', 1)
                            cookies[key] = value
                logger.info(
                    "调用菜单关键词API url=%s payload_sample=%s headers=%s cookies_keys=%s",
                    url,
                    {"menus_count": len(menus)},
                    headers,
                    list(cookies.keys()),
                )

                resp = await client.post(url, json=payload, headers=headers, cookies=cookies)
                resp.raise_for_status()
                data = resp.json()
                raw = []
                if isinstance(data, dict) and data.get("result"):
                    raw = data.get("result", data).get("dataList")
                result: Dict[str, List[str]] = {}

                # 目标格式：list[{menu_name: [kws]}]
                if isinstance(raw, list):
                    for item in raw:
                        if not isinstance(item, dict):
                            continue
                        if len(item) == 1:
                            k, v = next(iter(item.items()))
                            if isinstance(k, str) and isinstance(v, list):
                                kws = [str(x).strip() for x in v if isinstance(x, (str, int)) and str(x).strip()]
                                if kws:
                                    result[k] = kws
                        else:
                            # 兼容 {"menu":"名称","keywords":[...]} 结构
                            m = item.get("menu")
                            v = item.get("keywords")
                            if isinstance(m, str) and isinstance(v, list):
                                kws = [str(x).strip() for x in v if isinstance(x, (str, int)) and str(x).strip()]
                                if kws:
                                    result[m] = kws
                elif isinstance(raw, dict):
                    # 兼容 dict 直接返回 {menu: [kws]}
                    for k, v in raw.items():
                        if isinstance(k, str) and isinstance(v, list):
                            kws = [str(x).strip() for x in v if isinstance(x, (str, int)) and str(x).strip()]
                            if kws:
                                result[k] = kws
                return result
        except Exception as e:
            logger.error(f"从外部接口获取菜单关键词失败: {str(e)}")
            return {}

    @classmethod
    async def build_menu_keywords(cls, menus: List[str]) -> Dict[str, List[str]]:
        """
        结合本地关键词生成逻辑与实时接口数据，构建菜单关键词映射。

        注意：不会在类属性中缓存外部接口返回的数据，每次调用都会重新请求。
        """
        if not menus:
            return {}

        keyword_map: Dict[str, List[str]] = {}

        def _deduplicate(items: List[str]) -> List[str]:
            seen: Set[str] = set()
            deduped: List[str] = []
            for item in items:
                value = str(item).strip()
                if not value or value in seen:
                    continue
                seen.add(value)
                deduped.append(value)
            return deduped

        # 本地生成基础关键词
        for menu_name in menus:
            local_keywords = cls._extract_keywords(menu_name)
            keyword_map[menu_name] = _deduplicate(local_keywords if isinstance(local_keywords, list) else [menu_name]) or [menu_name]

        # 合并外部接口返回的关键词
        external_map = await cls._fetch_external_menu_keywords(menus)

        def _merge_into(target: str, kws: List[str]):
            if not target:
                return
            base = keyword_map.setdefault(target, [])
            existing = set(base)
            for kw in kws:
                if isinstance(kw, (str, int)):
                    value = str(kw).strip()
                    if value and value not in existing:
                        base.append(value)
                        existing.add(value)

        if external_map:
            for menu_name, kws in external_map.items():
                if not isinstance(menu_name, str) or not isinstance(kws, list):
                    continue
                normalized_name = menu_name.strip()
                if not normalized_name:
                    continue
                cleaned_keywords = [str(x).strip() for x in kws if isinstance(x, (str, int)) and str(x).strip()]
                if not cleaned_keywords:
                    continue
                _merge_into(normalized_name, cleaned_keywords)
                if "-" in normalized_name:
                    last = normalized_name.split("-")[-1].strip()
                    if last:
                        _merge_into(last, cleaned_keywords)

        return keyword_map

    @classmethod
    def _extract_keywords(cls, menu_name: str) -> List[str]:
        """
        从菜单名称中提取关键词
        
        支持完整路径格式（如"食堂管理-菜品管理-档口管理"）：
        1. 完整路径
        2. 各个层级的名称（第一级、第二级、第三级）
        3. 去除常见后缀后的名称
        4. 提取核心词汇（2-4字）
        5. 提取单个有意义的字
        
        策略：
        1. 完整菜单名/完整路径
        2. 如果包含"-"，提取各个层级的名称
        3. 去除常见后缀（如"管理"、"配置"、"分析"等）
        4. 提取核心词汇（2-4字）
        5. 提取单个字（如果是有意义的字）
        """
        keywords = [menu_name]  # 完整名称/完整路径
        
        # 如果包含"-"，说明是完整路径，提取各个层级
        if "-" in menu_name:
            parts = menu_name.split("-")
            # 添加各个层级
            for part in parts:
                if part and part not in keywords:
                    keywords.append(part)
            
            # 添加最后一级（最常用的匹配目标）
            if len(parts) > 0:
                last_part = parts[-1]
                if last_part and last_part not in keywords:
                    keywords.append(last_part)
        
        # 对每个部分（完整路径或单个名称）提取关键词
        parts_to_process = [menu_name]
        if "-" in menu_name:
            parts_to_process.extend(menu_name.split("-"))
        
        for part in parts_to_process:
            if not part:
                continue
                
            # 去除常见后缀
            suffixes = ['管理', '配置', '分析', '统计', '记录', '查询', '大屏', '中心', '系统', '设置']
            for suffix in suffixes:
                if part.endswith(suffix):
                    keyword = part[:-len(suffix)]
                    # 只添加长度>=2的关键词，避免单字符
                    if keyword and len(keyword) >= 2 and keyword not in keywords:
                        keywords.append(keyword)
            
            # 提取核心词汇（2-4字）
            # 使用正则表达式提取连续的汉字
            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', part)
            for char_seq in chinese_chars:
                # 提取2-4字的子串
                for length in [2, 3, 4]:
                    for i in range(len(char_seq) - length + 1):
                        keyword = char_seq[i:i+length]
                        if keyword not in keywords and len(keyword) >= 2:
                            keywords.append(keyword)
            
            # # 提取单个有意义的字（排除常见无意义字）
            # meaningless_chars = ['的', '和', '与', '或', '及', '等', '中', '在', '是', '有', '为', '被', '-']
            # for char in part:
            #     if '\u4e00' <= char <= '\u9fff' and char not in meaningless_chars:
            #         if char not in keywords:
            #             keywords.append(char)
        
        return list(set(keywords))  # 去重
    
    @classmethod
    def get_action_id_by_menu(cls, menu_name: str) -> int:
        """
        根据中文菜单名称获取对应的 menu_id（未配置返回 -1）
        
        Args:
            menu_name: 第三级菜单名称或完整路径
            
        Returns:
            menu_id，如果未找到返回 -1
        """
        # 如果传入的是完整路径，提取第三级名称
        if "-" in menu_name:
            menu_name = menu_name.split("-")[-1]
        return cls._menu_to_action_id.get(menu_name, -1)

    @classmethod
    async def ensure_menu_mapping(cls, user_id: Optional[int] = None, department_id: Optional[int] = None, session_id: Optional[str] = None) -> None:
        """
        懒加载：当 `_menu_to_action_id` 为空时，从 API 拉取并构建映射。
        """
        if not cls._menu_to_action_id:
            await cls._fetch_menus_from_api(user_id, department_id, session_id)

    @classmethod
    async def aget_action_id_by_menu(
        cls,
        menu_name: str,
        user_id: Optional[int] = None,
        department_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> int:
        """
        异步版本：确保映射已加载后再获取 action/menu_id。
        """
        await cls.ensure_menu_mapping(user_id=user_id, department_id=department_id, session_id=session_id)
        if "-" in menu_name:
            menu_name = menu_name.split("-")[-1]
        return cls._menu_to_action_id.get(menu_name, -1)
    
    @classmethod
    def get_full_path_by_menu(cls, menu_name: str) -> Optional[str]:
        """
        根据第三级菜单名称获取完整路径
        
        Args:
            menu_name: 第三级菜单名称或完整路径（如果是完整路径则直接返回）
            
        Returns:
            完整路径字符串，如果未找到返回 None
        """
        # 如果已经是完整路径，直接返回
        if "-" in menu_name:
            return menu_name
        return cls._menu_to_full_path.get(menu_name)
    
    @classmethod
    async def refresh_menu_mapping(cls) -> bool:
        """
        手动刷新菜单映射，从API获取最新的菜单数据并更新 _menu_to_action_id
        返回 True 表示成功，False 表示失败
        """
        try:
            # 清除缓存，强制重新获取
            cls.clear_cache()
            # 调用API获取菜单并更新映射
            await cls._fetch_menus_from_api()
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"刷新菜单映射失败: {str(e)}")
            return False

    # =============== 映射构建工具 ===============
    @classmethod
    def reset_menu_mapping_from_tree(cls, menu_tree: Dict[str, Any]):
        """
        使用后端返回的完整菜单树 JSON 重建 `_menu_to_action_id`。
        规则：递归遍历所有 `children`，将每个节点的 `name` -> `id` 写入。
        注意：过滤掉 "Companies" 菜单。
        """
        mapping: Dict[str, int] = {}

        def walk(node: Dict[str, Any]):
            node_id = node.get("id")
            node_name = node.get("name")
            # 过滤 "Companies" 菜单
            if isinstance(node_name, str) and node_name == "Companies":
                return
            if isinstance(node_id, int) and isinstance(node_name, str) and node_name:
                mapping[node_name] = node_id
            for child in node.get("children", []) or []:
                if isinstance(child, dict):
                    walk(child)

        walk(menu_tree)
        cls._menu_to_action_id = mapping

    @classmethod
    def _parse_data_list_menu_structure(cls, data_list: List[Dict[str, Any]]):
        """
        解析 dataList 结构的三级菜单，构建第三级菜单名称到ID的映射
        
        结构：
        - first: { "title": "食堂管理", "first_id": 1150, "children": [...] }
        - second: { "title": "菜品管理", "second_id": 1168, "children": [...] }
        - third: { "title": "档口管理", "third_id": 1209, "menu_id": 1209, "action": 492 }
        
        映射规则：
        - key: 第三级菜单的 title（如 "档口管理"）
        - value: 第三级菜单的 menu_id（如 1209）
        
        注意：如果多个第三级菜单有相同的名称，后面的会覆盖前面的
        """
        mapping: Dict[str, int] = {}
        
        def walk_first_level(first_items: List[Dict[str, Any]]):
            """遍历第一级菜单"""
            for first_item in first_items:
                if not isinstance(first_item, dict):
                    continue
                
                first_title = first_item.get("title", "")
                first_children = first_item.get("children", []) or []
                
                if not first_title or not isinstance(first_children, list):
                    continue
                
                # 过滤 "Companies" 菜单
                if first_title == "Companies":
                    continue
                
                # 遍历第二级菜单
                walk_second_level(first_title, first_children)
        
        def walk_second_level(first_title: str, second_items: List[Dict[str, Any]]):
            """遍历第二级菜单"""
            for second_item in second_items:
                if not isinstance(second_item, dict):
                    continue
                
                second_title = second_item.get("title", "")
                second_children = second_item.get("children", []) or []
                
                if not second_title or not isinstance(second_children, list):
                    continue
                
                # 过滤 "Companies" 菜单（可能在第二级也存在）
                if second_title == "Companies":
                    continue
                
                # 遍历第三级菜单（叶子节点），传递第一级标题
                walk_third_level(first_title, second_children)
        
        def walk_third_level(first_title: str, third_items: List[Dict[str, Any]]):
            """遍历第三级菜单（叶子节点），保存第三级名称 -> menu_id 映射"""
            for third_item in third_items:
                if not isinstance(third_item, dict):
                    continue
                
                third_title = third_item.get("title", "")
                # 优先使用 menu_id，如果没有则使用 third_id
                menu_id = third_item.get("action")
                
                if not third_title:
                    continue
                
                # 过滤 "Companies" 菜单（可能在第三级也存在）
                if third_title == "Companies":
                    continue
                
                # 构建完整路径：第一级-第三级（去掉第二级）
                full_path = f"{first_title}-{third_title}"
                
                if isinstance(menu_id, int):
                    # 保存映射：第三级菜单名称 -> menu_id
                    mapping[third_title] = menu_id
                    # 保存完整路径映射：第三级菜单名称 -> 完整路径（第一级-第三级）
                    cls._menu_to_full_path[third_title] = full_path
                elif isinstance(menu_id, str):
                    # 如果 menu_id 是字符串，尝试转换为整数
                    try:
                        mapping[third_title] = int(menu_id)
                        cls._menu_to_full_path[third_title] = full_path
                    except (ValueError, TypeError):
                        pass
        
        # 开始遍历
        walk_first_level(data_list)
        
        # 更新映射
        cls._menu_to_action_id = mapping
    
    @classmethod
    def update_menu_mapping_from_children(cls, children: List[Dict[str, Any]]):
        """
        直接用一个 children 数组（每项含 id/name/children）来更新映射。
        注意：过滤掉 "Companies" 菜单。
        """
        mapping: Dict[str, int] = dict(cls._menu_to_action_id)

        def walk_list(nodes: List[Dict[str, Any]]):
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                node_id = node.get("id")
                node_name = node.get("name")
                # 过滤 "Companies" 菜单
                if isinstance(node_name, str) and node_name == "Companies":
                    continue
                if isinstance(node_id, int) and isinstance(node_name, str) and node_name:
                    mapping[node_name] = node_id
                children_nodes = node.get("children", []) or []
                if isinstance(children_nodes, list) and children_nodes:
                    walk_list(children_nodes)

        walk_list(children)
        cls._menu_to_action_id = mapping

