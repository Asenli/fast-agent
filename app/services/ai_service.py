"""
AI服务模块 - 使用DeepSeek API
"""
import json
import ast
import logging
import re
import httpx
from typing import List, Optional
from app.core.config import settings
from app.services.menu_service import MenuService
try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore
except Exception:  # 运行环境未安装也不阻塞，其它兜底逻辑会生效
    SentenceTransformer = None  # type: ignore
    util = None  # type: ignore


class AIService:
    """
    AI服务 - 菜单意图匹配引擎。

    优先级策略：
    1) 本地中文向量模型（`bge-small-zh` 或在线 `BAAI/bge-small-zh`）做相似度排序
    2) 失败或缺依赖则降级为关键词匹配（基于 `MenuService` 动态生成的关键词）
    3) 可选：DeepSeek API 带来的匹配（当前作为示例/备用路径）
    """
    _embedding_model = None  # SentenceTransformer 实例（延迟加载）
    
    @staticmethod
    async def match_menus(user_input: str, menus: List[str], menu_keywords: Optional[dict] = None, ai_mode: Optional[str] = None) -> List[str]:
        """
        使用AI匹配菜单，返回所有可能的匹配结果
        
        Args:
            user_input: 用户输入的文本
            menus: 菜单列表
            menu_keywords: 菜单关键词映射 {菜单名: [关键词列表]}
            
        Returns:
            匹配的菜单列表（按相关性排序）
        """
        try:
            # 通过请求参数控制匹配策略：
            # - ai_mode == 'deepseek'：调用 DeepSeek（返回单个，包装为列表），失败则兜底 simple
            # - 其他/默认：使用向量相似度匹配，失败兜底 simple
            if ai_mode and ai_mode.lower() == 'deepseek':
                deepseek_matched = await AIService._call_deepseek(user_input, menus)
                if deepseek_matched:
                    return [deepseek_matched]
                print(f"deepseek AI匹配失败")
                return []
                # return AIService._simple_match_multiple(user_input, menus)
            elif ai_mode and ai_mode.lower() == 'bge-small-zh':
                matched = AIService._embedding_match_multiple(user_input, menus, menu_keywords)
                return matched if matched else []
            else:
                matched = AIService._simple_match_multiple(user_input, menus)
                return matched if matched else []
        except Exception as e:
            print(f"AI匹配失败: {e}")
            # 降级方案：使用简单的关键词匹配
            return AIService._simple_match_multiple(user_input, menus)
    
    @staticmethod
    async def match_menu(user_input: str, menus: List[str]) -> Optional[str]:
        """
        使用AI匹配菜单（兼容旧接口，返回单个结果）
        
        Args:
            user_input: 用户输入的文本
            menus: 菜单列表
            
        Returns:
            匹配的菜单名称（单个）
        """
        menu_keywords = MenuService.get_all_menu_keywords()
        matched_menus = await AIService.match_menus(user_input, menus, menu_keywords)
        return matched_menus[0] if matched_menus else None
    
    @staticmethod
    def _keyword_match(user_input: str, menus: List[str], menu_keywords: dict) -> List[str]:
        """
        基于关键词的匹配（使用动态生成的分词，带评分排序）
        
        Args:
            user_input: 用户输入
            menus: 菜单列表
            menu_keywords: 菜单关键词映射
            
        Returns:
            匹配的菜单列表（按匹配度排序，只返回高分匹配）
        """
        scores = {}  # {菜单名: 匹配分数}
        
        for menu_name in menus:
            keywords = menu_keywords.get(menu_name, [menu_name])
            score = 0
            
            # 完整菜单名匹配得分最高
            if menu_name in user_input:
                score += 100
            
            # 关键词匹配，长关键词得分更高
            for keyword in keywords:
                if keyword in user_input:
                    # 关键词长度越长，得分越高（避免单字符过度匹配）
                    if len(keyword) >= 2:
                        score += len(keyword) * 10  # 2字=20分，3字=30分，4字=40分
                    elif len(keyword) == 1:
                        # 单字符只给1分（虽然已经移除了单字符，但保留以防万一）
                        score += 1
            
            if score > 0:
                scores[menu_name] = score
        
        # 按分数降序排序
        sorted_menus = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # 只返回分数大于等于20分的菜单（至少匹配了一个2字关键词或完整菜单名）
        return [menu for menu, score in sorted_menus if score >= 20]
    
    @staticmethod
    async def _call_deepseek(user_input: str, menus: List[str]) -> Optional[str]:
        """
        调用 DeepSeek API 获取匹配结果（示例）。

        返回内容通常是包含候选的文本，方法内会尝试解析为列表或直接匹配菜单名。
        失败时返回 None，不影响主流程（有降级策略）。
        """
        try:
            prompt = f"你是一个智能系统，只需根据用户输入去理解想打开哪个菜单，从以下列表中返回一个或者多个最相关项： {menus}。 输入：{user_input} 请直接输出 Python 列表格式，不要解释和多余的，也不要编造。"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.AI_BASE_URL}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.AI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.AI_MODEL,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 100
                    }
                )
                response.raise_for_status()
                result = response.json()
                content_list = result['choices'][0]['message']['content']
                content_list = json.loads(content_list) if isinstance(content_list, str) else content_list
                return AIService._parse_ai_response(content_list, menus)
        except httpx.HTTPError as e:
            print(f"DeepSeek API HTTP错误: {e}")
            return None
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return None
    
    @staticmethod
    def _parse_ai_response(content: List[str], menus: List[str]) -> Optional[str]:
        """解析AI返回结果"""
        try:
            # 若 content 已经是列表（上游直接返回多个候选）
            if isinstance(content, list):  # type: ignore[unreachable]
                parsed_items: List[str] = [str(x).strip() for x in content if str(x).strip()]
                for token in parsed_items:
                    if token in menus:
                        return token
                for token in parsed_items:
                    if len(token) >= 2:
                        for menu in menus:
                            if token in menu or menu in token:
                                return menu
                return None

            # 清理内容，移除可能的markdown代码块标记
            content = content.strip()
            if content.startswith("```"):
                # 移除代码块标记
                lines = content.split('\n')
                content = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            # 1) 优先尝试解析为 JSON 列表
            parsed_items: List[str] = []
            try:
                loaded = json.loads(content)
                if isinstance(loaded, list):
                    parsed_items = [str(x).strip() for x in loaded]
                elif isinstance(loaded, dict) and 'items' in loaded and isinstance(loaded['items'], list):
                    parsed_items = [str(x).strip() for x in loaded['items']]
            except Exception:
                pass

            # 2) 尝试解析 Python 列表字面量，如 ['a','b']
            if not parsed_items:
                try:
                    lit = ast.literal_eval(content)
                    if isinstance(lit, list):
                        parsed_items = [str(x).strip() for x in lit]
                except Exception:
                    pass

            # 3) 正则提取 [ ... ] 中的内容并按常见分隔符切分
            if not parsed_items:
                match = re.search(r'\[(.*?)\]', content, re.S)
                if match:
                    list_content = match.group(1)
                    # 统一分隔符：逗号/顿号/分号/换行
                    raw = re.split(r"[,，、;；\n]", list_content)
                    parsed_items = [re.sub(r"^[\'\"\s]+|[\'\"\s]+$", "", x) for x in raw if x and x.strip()]

            # 4) 如果仍不是列表，按分隔符直接拆分整段文本
            if not parsed_items:
                raw = re.split(r"[,，、;；\n\t]", content)
                parsed_items = [x.strip().strip('"').strip("'") for x in raw if x and x.strip()]

            # 优先返回第一个精确命中的菜单
            for token in parsed_items:
                if token in menus:
                    return token

            # 次优：token 与菜单存在包含关系（保持原顺序，尽量按 AI 给的优先级）
            for token in parsed_items:
                if len(token) >= 2:
                    for menu in menus:
                        if token in menu or menu in token:
                            return menu

            # 最后兜底：直接在整段内容中寻找任意菜单名
            for menu in menus:
                if menu in content:
                    return menu
            
            return None
        except Exception as e:
            print(f"解析AI响应失败: {e}")
            return None
    
    @staticmethod
    def _embedding_match_multiple(user_input: str, menus: List[str], menu_keywords: Optional[dict] = None) -> List[str]:
        """
        使用中文向量模型进行相似度匹配，返回多个候选（按相似度排序）。

        阈值与行为（进一步优化）：
        - 对短词（<=2字）采用更激进的策略：如果分数差距不够大，只返回第一个
        - 结合关键词过滤，过滤掉明显不相关的菜单
        - 返回分数 >= max(0.45, 最高分-0.02) 的项，最多 3 项
        - 任意异常时返回空列表，让上层走关键词降级逻辑
        """
        import os
        try:
            if not menus or not user_input:
                return []

            # 若运行环境没有安装依赖，则跳过此方案
            if SentenceTransformer is None:
                return []

            # 延迟加载模型（进程级缓存）
            if AIService._embedding_model is None:
                # 优先从项目根目录下的本地模型目录加载：./bge-small-zh
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                local_model_dir = os.path.join(project_root, "bge-small-zh")
                if os.path.isdir(local_model_dir):
                    AIService._embedding_model = SentenceTransformer(local_model_dir)
                else:
                    logging.error("未找到本地模型目录 bge-small-zh，无法加载向量模型")
                    raise Exception("未找到本地模型目录，请检查项目根目录是否存在 bge-small-zh 目录")

            model = AIService._embedding_model

            # 计算向量（规范化后使用余弦相似度）
            menu_vecs = model.encode(menus, normalize_embeddings=True)
            query_vec = model.encode([user_input], normalize_embeddings=True)[0]

            scores_tensor = util.cos_sim(query_vec, menu_vecs)[0]
            scores = scores_tensor.tolist()

            # 根据分数排序
            indices = list(range(len(menus)))
            indices.sort(key=lambda i: scores[i], reverse=True)

            if not indices:
                return []

            top1 = indices[0]
            if len(indices) == 1:
                return [menus[top1]]

            max_score = scores[top1]
            second_score = scores[indices[1]] if len(indices) > 1 else 0
            gap = max_score - second_score

            query_len = len(user_input.strip())
            
            # 设置阈值参数（平衡严格性和相关性）
            if query_len <= 2:
                # 短词：使用中等严格的阈值
                base_threshold = 0.40  # 适中的基础阈值
                delta = 0.05  # 适中的窗口，允许返回多个相关结果
            else:
                # 长词：相对宽松
                base_threshold = 0.38
                delta = 0.05
            
            threshold = max(base_threshold, max_score - delta)
            result = [menus[i] for i in indices if scores[i] >= threshold]

            # 使用关键词进行二次过滤（过滤明显不相关的结果）
            if menu_keywords and result:
                filtered_result = []
                
                for menu in result:
                    # 检查菜单名是否直接包含用户输入（如"配送"包含在"配送包管理"中）
                    if user_input in menu:
                        filtered_result.append(menu)
                        continue
                    
                    # 检查关键词：如果关键词包含用户输入，也认为是相关的
                    keywords = menu_keywords.get(menu, [])
                    matched = False
                    for keyword in keywords:
                        # 用户输入包含在关键词中（如"配送"在"配送包"中）
                        if user_input in keyword:
                            matched = True
                            break
                    
                    if matched:
                        filtered_result.append(menu)
                
                # 如果关键词过滤后还有结果，使用过滤后的
                # 如果过滤后没有结果，说明可能是向量匹配不够准确，但保留原始结果（让关键词过滤不要过于严格）
                if filtered_result:
                    result = filtered_result
                # 如果过滤后没有结果，保留原始结果（可能是关键词提取不完整）

            # 对于短词，如果最高分明显高于其他结果，且分数足够高，可以考虑只返回第一个
            # 但只有在分数差距很大且最高分很高时才这样做
            if query_len <= 2:
                # 只有当最高分很高（>=0.65）且分数差距很大（>=0.15）时，才只返回第一个
                # 这样可以保留多个相关结果（如"配送"相关的多个菜单）
                if max_score >= 0.65 and gap >= 0.15:
                    result = [menus[top1]]
                # 如果最高分较低（<0.45），说明整体匹配度不高，但如果有多个相关结果，还是返回它们
                elif max_score < 0.45:
                    # 只保留分数较高的前3个
                    result = result[:3]
            else:
                # 长词：如果分数差距很大，只返回第一个
                if gap >= 0.12 and max_score >= 0.60:
                    result = [menus[top1]]

            # 限制返回数量：短词至少返回3个（如果有多于3个的相关结果），最多5个
            # 长词最多5个
            max_results = 5
            min_results = 3 if query_len <= 2 else 1
            
            # 如果结果数量少于最小要求，且还有更多候选，尝试放宽阈值
            if len(result) < min_results and len(indices) > len(result):
                # 放宽阈值，尝试获取更多结果
                relaxed_threshold = max(0.35, max_score - 0.10)
                relaxed_result = [menus[i] for i in indices if scores[i] >= relaxed_threshold]
                
                # 对放宽的结果也进行关键词过滤
                if menu_keywords and relaxed_result:
                    relaxed_filtered = []
                    for menu in relaxed_result:
                        if user_input in menu:
                            relaxed_filtered.append(menu)
                            continue
                        keywords = menu_keywords.get(menu, [])
                        for keyword in keywords:
                            if user_input in keyword:
                                relaxed_filtered.append(menu)
                                break
                    if relaxed_filtered:
                        result = relaxed_filtered[:max_results]
                    else:
                        result = relaxed_result[:max_results]
                else:
                    result = relaxed_result[:max_results]
            
            result = result[:max_results] if result else [menus[top1]]
            return result
        except Exception:
            # 任意异常时回退，让上层继续走关键词方案
            return []
    
    @staticmethod
    def _simple_match_multiple(user_input: str, menus: List[str]) -> List[str]:
        """
        简单关键词匹配（降级方案），返回多个匹配结果（带评分排序）
        
        Args:
            user_input: 用户输入
            menus: 菜单列表
            
        Returns:
            匹配的菜单列表（按相关性排序，只返回高分匹配）
        """
        scores = {}  # {菜单名: 匹配分数}
        
        # 使用动态生成的关键词
        menu_keywords = MenuService.get_all_menu_keywords()
        
        # 检查每个菜单
        for menu in menus:
            keywords = menu_keywords.get(menu, [menu])
            score = 0
            exact_match = False  # 标记是否有精确匹配
            
            # 完整菜单名匹配得分最高
            if user_input in menu or menu in user_input:
                score += 100
                exact_match = True
            
            # 关键词匹配，优先精确匹配（用户输入在关键词中）
            for keyword in keywords:
                # 精确匹配：用户输入完整包含在关键词中（得分更高）
                if user_input in keyword:
                    score += len(user_input) * 15  # 精确匹配：按用户输入长度给分，4字=60分
                    exact_match = True
                # 部分匹配：关键词在用户输入中（得分较低）
                elif keyword in user_input:
                    # 只有长关键词才给分，避免"管理"这样的通用词匹配太多
                    if len(keyword) >= len(user_input):
                        # 关键词长度>=用户输入长度，给较高分
                        score += len(keyword) * 10
                    elif len(keyword) >= 3:
                        # 关键词长度>=3，给中等分
                        score += len(keyword) * 5
                    else:
                        # 短关键词（2字）给低分，但只在没有精确匹配时考虑
                        if not exact_match and len(keyword) >= 2:
                            score += len(keyword) * 3
            
            if score > 0:
                scores[menu] = score
        
        # 按分数降序排序
        sorted_menus = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_menus:
            return []
        
        # 如果只有一个匹配结果，直接返回
        if len(sorted_menus) == 1:
            return [sorted_menus[0][0]] if sorted_menus else []

        matched = [menu for menu, score in sorted_menus ]

        # if not matched:
        #     return []
        # 检查最高分和次高分的差距
        max_score = sorted_menus[0][1]
        second_score = sorted_menus[1][1] if len(sorted_menus) > 1 else 0
        score_gap = max_score - second_score
        
        # 如果分数差距>=40分（说明有明显的精确匹配），只返回第一个
        if score_gap >= 40:
            return [sorted_menus[0][0]]
        
        # 如果分数差别不大，保持现在逻辑，返回所有符合条件的匹配
        return matched
    
    @staticmethod
    def _simple_match(user_input: str, menus: List[str]) -> Optional[str]:
        """
        简单关键词匹配（兼容旧接口，返回单个结果）
        
        Args:
            user_input: 用户输入
            menus: 菜单列表
            
        Returns:
            匹配的菜单名称（单个）
        """
        matched = AIService._simple_match_multiple(user_input, menus)
        return matched[0] if matched else None

