# 智能菜单导航系统使用说明

## 功能概述

本系统实现了基于AI的智能菜单导航功能，支持：
1. 接收文本指令
2. 自动匹配菜单（使用DeepSeek AI）
3. 权限验证
4. WebSocket实时消息推送
5. 前端自动执行菜单跳转

## API端点

### 1. 发送语音指令

**POST** `/api/v1/voice/command`

请求体：
```json
{
  "text": "我希望操作菜谱，帮我打开菜谱",
  "user_id": 1
}
```

响应：
```json
{
  "success": true,
  "message": "正在为您打开商品菜谱",
  "menu": "商品菜谱",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. 获取菜单列表

**GET** `/api/v1/voice/menus`

响应：
```json
{
  "menus": ["预警中心", "食材调价管理", "营养膳食", "商品菜谱", "单位配置", "财务管理"],
  "count": 6
}
```

### 3. WebSocket连接

**WS** `/api/v1/ws/{user_id}`

连接后可以接收消息：
```json
{
  "type": "menu_navigation",
  "menu": "商品菜谱",
  "user_id": 1,
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "command": "我希望操作菜谱，帮我打开菜谱",
    "matched_menu": "商品菜谱"
  }
}
```

### 4. 检查WebSocket连接状态

**GET** `/api/v1/ws/status/{user_id}`

响应：
```json
{
  "user_id": 1,
  "connected": true
}
```

## 使用流程

### 后端流程

1. 接收文本指令 → `POST /api/v1/voice/command`
2. 获取菜单列表（带缓存）
3. 调用DeepSeek AI分析匹配菜单
4. 验证用户权限
5. 推送消息到WebSocket

### 前端流程

1. 连接WebSocket → `ws://localhost:8001/api/v1/ws/{user_id}`
2. 发送文本指令 → `POST /api/v1/voice/command`
3. 接收WebSocket消息
4. 执行菜单跳转操作

## 前端示例代码

```javascript
// 1. 连接WebSocket
const ws = new WebSocket('ws://localhost:8001/api/v1/ws/1');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'menu_navigation') {
    // 执行菜单跳转
    navigateToMenu(message.menu);
    
    // 发送确认消息
    ws.send(JSON.stringify({
      type: 'ack',
      menu: message.menu
    }));
  }
};

// 2. 发送文本指令
async function sendCommand(text) {
  const response = await fetch('http://localhost:8001/api/v1/voice/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, user_id: 1 })
  });
  return await response.json();
}

// 使用示例
sendCommand('我希望操作菜谱，帮我打开菜谱');
```

## 配置说明

在 `app/core/config.py` 中配置：

```python
# AI配置 - DeepSeek
AI_API_KEY: str = "sk-ba87253c34f74a7dbb790fb5776c53eb"
AI_BASE_URL: str = "https://api.deepseek.com"
AI_MODEL: str = "deepseek-chat"

# 缓存配置
CACHE_TTL: int = 3600  # 菜单缓存TTL（秒）
```

## 测试方法

1. 启动服务：
```bash
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

2. 打开测试页面：
   - 使用提供的 `test_voice_api.html` 文件
   - 或者在浏览器中访问该文件

3. 测试步骤：
   - 点击"连接WebSocket"按钮
   - 输入文本指令（如："我希望操作菜谱，帮我打开菜谱"）
   - 点击"发送指令"按钮
   - 查看日志输出和WebSocket消息

## 错误处理

系统会返回以下错误情况：

1. **未匹配到菜单**：
   ```json
   {
     "success": false,
     "message": "小智还在学习中...，未理解到您的意思",
     "menu": null
   }
   ```

2. **无权限**：
   ```json
   {
     "success": false,
     "message": "您无操作权限",
     "menu": null
   }
   ```

## 扩展开发

### 自定义菜单数据源

修改 `app/services/menu_service.py` 中的 `_fetch_menus_from_api()` 方法：

```python
@staticmethod
async def _fetch_menus_from_api() -> List[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://your-menu-api/menus")
        data = response.json()
        return [menu['name'] for menu in data]
```

### 自定义权限验证

修改 `app/services/permission_service.py` 中的 `check_menu_permission()` 方法：

```python
@staticmethod
async def check_menu_permission(user_id: int, menu_name: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://your-permission-api/permissions/{user_id}",
            params={"menu": menu_name}
        )
        return response.json().get('has_permission', False)
```

## 注意事项

1. 确保DeepSeek API密钥有效
2. WebSocket连接需要保持活跃，否则无法接收消息
3. 菜单缓存默认1小时，可通过 `CACHE_TTL` 配置
4. 如果AI调用失败，系统会自动降级到关键词匹配

