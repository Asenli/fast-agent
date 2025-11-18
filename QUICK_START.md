# 快速启动指南

## 1. 安装依赖

确保已安装所有必要的依赖：

```bash
pip install -r requirements.txt
```

或者使用 Poetry：

```bash
poetry install
```

## 2. 配置环境变量（可选）

如果需要从环境变量读取配置，创建 `.env` 文件：

```env
# 基础
HOST=0.0.0.0
PORT=8001
DEBUG=False

# AI（DeepSeek）
AI_API_KEY=替换为你的Key
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat

# 菜单 API
MENU_API_BASE_URL=http://127.0.0.1:8090
MENU_API_COOKIE=
CACHE_TTL=3600

# WebSocket
WS_HEARTBEAT_INTERVAL=30
```

## 3. 启动服务

```bash
python main.py
```

或者使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## 4. 测试API

### 使用 curl 测试：

```bash
# 发送文本指令
curl -X POST "http://localhost:8001/api/v1/voice/command" \
  -H "Content-Type: application/json" \
  -d '{"text": "我希望操作菜谱，帮我打开菜谱", "user_id": 1}'

# 获取菜单列表
curl "http://localhost:8001/api/v1/voice/menus"

# 检查WebSocket状态
curl "http://localhost:8001/api/v1/ws/status/1"
```

### 使用测试页面：

1. 在浏览器中打开 `test_voice_api.html`
2. 点击"连接WebSocket"按钮
3. 输入文本指令并发送
4. 查看日志输出

## 5. API文档

启动服务后，访问：
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 6. WebSocket测试

可以使用在线工具或编写简单的客户端：

```javascript
const ws = new WebSocket('ws://localhost:8001/api/v1/ws/1');
ws.onmessage = (event) => {
  console.log('收到消息:', JSON.parse(event.data));
};
```

可发送心跳：

```javascript
ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
```

## 功能说明

### 完整流程

1. **接收文本指令** → `POST /api/v1/voice/command`
2. **获取菜单列表** → 从缓存或API获取
3. **AI分析匹配** → 优先向量相似度，本地模型；失败或缺依赖时降级关键词匹配；也支持 DeepSeek 接口
4. **权限验证** → 检查用户权限
5. **推送消息** → 通过WebSocket发送
6. **前端接收** → 执行菜单跳转

### 错误处理

- 未匹配到菜单 → 返回友好提示
- 无权限 → 返回权限错误
- AI调用失败 → 自动降级到关键词匹配

## 扩展开发

### 自定义菜单数据源

编辑 `app/services/menu_service.py` 中的 `_fetch_menus_from_api()` 方法。

### 自定义权限验证

编辑 `app/services/permission_service.py` 中的 `check_menu_permission()` 方法。

### 启用本地中文向量模型（可选）

1. 将 `bge-small-zh/` 模型目录放到项目根目录
2. 安装 `sentence-transformers`
3. 无网络或接口不可用时，仍可完成多候选匹配

## 注意事项

1. 生产环境不要把密钥写入代码，改用环境变量
2. WebSocket 需保持连接；断开将无法收到导航消息
3. 菜单缓存默认1小时，可用 `CACHE_TTL` 调整
4. AI 调用失败会自动降级，不影响核心流程
5. 如外部菜单接口结构变更，请同步调整 `menu_service.py` 的解析逻辑

