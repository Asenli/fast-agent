# FastAPI 服务项目

一个基于 FastAPI 的现代化 Web 服务项目，提供了完整的项目结构和最佳实践。

pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple

poetry install   

## 📁 项目结构

```
fast-agent/
├── app/                    # 应用主目录
│   ├── __init__.py
│   ├── core/              # 核心配置模块
│   │   ├── __init__.py
│   │   └── config.py      # 应用配置
│   ├── routers/           # API 路由模块
│   │   ├── __init__.py
│   │   ├── api.py         # 主路由注册
│   │   ├── items.py       # 商品路由
│   │   └── users.py       # 用户路由
│   ├── models/            # 数据模型（数据库模型）
│   │   └── __init__.py
│   ├── schemas/           # Pydantic 模式定义
│   │   ├── __init__.py
│   │   ├── item.py        # 商品模式
│   │   └── user.py        # 用户模式
│   ├── services/          # 业务逻辑服务层
│   │   ├── __init__.py
│   │   └── item_service.py
│   └── utils/             # 工具函数
│       ├── __init__.py
│       └── logging.py     # 日志工具
├── tests/                 # 测试目录
│   ├── __init__.py
│   └── test_main.py       # 主应用测试
├── main.py                # 应用入口文件
├── requirements.txt       # Python 依赖
├── pyproject.toml         # 项目配置
├── env.example            # 环境变量示例
├── .gitignore            # Git 忽略文件
└── README.md             # 项目说明文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- pip 或 poetry（推荐）

### 2. 安装依赖

使用 pip 安装：

```bash
pip install -r requirements.txt
```

或使用 poetry：

```bash
poetry install
```

### 3. 配置环境变量

复制 `env.example` 文件为 `.env` 并修改配置：

```bash
cp env.example .env
```

或者在 Windows 上：

```bash
copy env.example .env
```

编辑 `.env` 文件，根据需要修改配置项。

### 4. 运行服务

开发模式运行：

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 5. 访问 API 文档

启动服务后，访问以下地址：

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- API 根路径: http://localhost:8001/

## 🐧 Linux 生产环境部署

### 前置要求

- Linux 系统（Ubuntu 20.04+ / CentOS 7+ / Debian 10+）
- Docker 和 Docker Compose（推荐方式）
- 或 Python 3.9+ 和 pip（直接部署方式）

### 方式一：Docker 部署（推荐）

#### 1. 安装 Docker 和 Docker Compose

**Ubuntu/Debian:**
```bash
# 更新包索引
sudo apt-get update

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

**CentOS/RHEL:**
```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 准备项目文件

```bash
# 克隆或上传项目到服务器
cd /opt
git clone <your-repo-url> fast-agent
cd fast-agent

# 或使用 scp 上传项目文件
# scp -r fast-agent/ user@server:/opt/
```

#### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑环境变量（使用 vim 或 nano）
vim .env
```

在 `.env` 文件中配置必要的环境变量，特别是：
- `AI_API_KEY`: 你的 DeepSeek API 密钥
- `MENU_API_BASE_URL`: 菜单服务地址
- `MENU_API_COOKIE`: 菜单服务 Cookie（如需要）
- `DEBUG=False`: 生产环境关闭调试模式

#### 4. 使用 Docker Compose 部署

```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

#### 5. 验证部署

```bash
# 检查健康状态
curl http://localhost:8001/health

# 查看容器日志
docker-compose logs fast-agent

# 进入容器调试（如需要）
docker-compose exec fast-agent bash
```

#### 6. 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 查看更新日志
docker-compose logs -f
```

#### 7. 清理镜像和容器

**方式一：使用清理脚本（推荐）**

```bash
# 赋予执行权限
chmod +x docker-clean.sh

# 运行清理脚本（交互式菜单）
./docker-clean.sh
```

**方式二：使用命令行**

```bash
# 停止并删除容器（保留镜像）
docker-compose down

# 停止并删除容器和网络（保留镜像）
docker-compose down --remove-orphans

# 删除容器、网络和镜像
docker-compose down --rmi all

# 删除容器、网络、镜像和卷（谨慎使用）
docker-compose down --rmi all -v

# 仅删除未使用的镜像（清理悬空镜像）
docker image prune -f

# 删除所有未使用的镜像（包括有标签的）
docker image prune -a -f

# 完整清理：删除所有未使用的容器、网络、镜像和构建缓存
docker system prune -a -f

# 查看镜像列表
docker images | grep fast-agent

# 手动删除指定镜像
docker rmi fast-agent_fast-agent
# 或
docker rmi $(docker images fast-agent* -q)
```

### 方式二：直接部署（不使用 Docker）

#### 1. 安装 Python 和依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip python3-venv

# CentOS/RHEL
sudo yum install -y python39 python39-pip
```

#### 2. 创建虚拟环境

```bash
cd /opt/fast-agent
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装项目依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
pip install sentence-transformers>=2.6.1
```

#### 4. 配置环境变量

```bash
cp env.example .env
vim .env  # 编辑配置
```

#### 5. 使用 systemd 管理服务

创建 systemd 服务文件：

```bash
sudo vim /etc/systemd/system/fast-agent.service
```

添加以下内容：

```ini
[Unit]
Description=FastAPI Agent Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/fast-agent
Environment="PATH=/opt/fast-agent/venv/bin"
ExecStart=/opt/fast-agent/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start fast-agent

# 设置开机自启
sudo systemctl enable fast-agent

# 查看状态
sudo systemctl status fast-agent

# 查看日志
sudo journalctl -u fast-agent -f
```

#### 6. 使用 Gunicorn（生产环境推荐）

安装 Gunicorn：

```bash
pip install gunicorn
```

修改 systemd 服务文件中的 ExecStart：

```ini
ExecStart=/opt/fast-agent/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001 \
    --access-logfile - \
    --error-logfile -
```

### 方式三：使用 Nginx 反向代理（可选）

#### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt-get install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
```

#### 2. 配置 Nginx

创建配置文件：

```bash
sudo vim /etc/nginx/sites-available/fast-agent
```

添加以下配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或 IP

    # 日志
    access_log /var/log/nginx/fast-agent-access.log;
    error_log /var/log/nginx/fast-agent-error.log;

    # 反向代理到 FastAPI
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8001/health;
        access_log off;
    }
}
```

启用配置：

```bash
# Ubuntu/Debian
sudo ln -s /etc/nginx/sites-available/fast-agent /etc/nginx/sites-enabled/

# CentOS/RHEL（直接创建配置文件）
sudo vim /etc/nginx/conf.d/fast-agent.conf
# 然后粘贴上面的配置内容

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 3. 配置 SSL（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx  # Ubuntu/Debian
# 或
sudo yum install -y certbot python3-certbot-nginx      # CentOS/RHEL

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 防火墙配置

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 8001/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### 监控和维护

#### 查看服务状态

```bash
# Docker 方式
docker-compose ps
docker-compose logs -f --tail=100

# systemd 方式
sudo systemctl status fast-agent
sudo journalctl -u fast-agent -n 100 -f
```

#### 性能监控

```bash
# 查看资源使用
docker stats fast-agent  # Docker 方式
# 或
top -p $(pgrep -f "uvicorn main:app")  # 直接部署方式

# 查看端口占用
sudo netstat -tlnp | grep 8001
# 或
sudo ss -tlnp | grep 8001
```

#### 备份和恢复

```bash
# 备份项目文件
tar -czf fast-agent-backup-$(date +%Y%m%d).tar.gz /opt/fast-agent

# 备份环境变量（重要！）
cp /opt/fast-agent/.env /opt/fast-agent/.env.backup
```

### 常见问题排查

#### 1. 服务无法启动

```bash
# 检查端口是否被占用
sudo lsof -i :8001
# 或
sudo netstat -tlnp | grep 8001

# 检查日志
docker-compose logs fast-agent  # Docker 方式
sudo journalctl -u fast-agent -n 50  # systemd 方式

# 检查环境变量
docker-compose exec fast-agent env  # Docker 方式
```

#### 2. 无法访问服务

```bash
# 检查防火墙
sudo ufw status  # Ubuntu/Debian
sudo firewall-cmd --list-all  # CentOS/RHEL

# 检查服务是否运行
docker-compose ps  # Docker 方式
sudo systemctl status fast-agent  # systemd 方式

# 测试本地连接
curl http://localhost:8001/health
```

#### 3. 模型加载失败

```bash
# 检查模型文件是否存在
ls -lh /opt/fast-agent/bge-small-zh/

# 检查磁盘空间
df -h

# 查看详细错误日志
docker-compose logs fast-agent | grep -i error
```

#### 4. 内存不足

```bash
# 查看内存使用
free -h
docker stats  # Docker 方式

# 如果使用 Docker，可以限制容器内存
# 在 docker-compose.yml 中添加：
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

#### 5. WebSocket 连接失败

```bash
# 检查 Nginx 配置（如果使用）
sudo nginx -t

# 检查防火墙是否允许 WebSocket
# 确保 Nginx 配置中包含 WebSocket 相关设置

# 测试 WebSocket 连接
wscat -c ws://localhost:8001/api/v1/ws/1
```

### 生产环境最佳实践

1. **安全配置**
   - 使用强密码和 API 密钥
   - 定期更新依赖包
   - 启用 HTTPS
   - 配置适当的 CORS 策略
   - 使用非 root 用户运行服务

2. **性能优化**
   - 使用 Gunicorn + Uvicorn workers（直接部署）
   - 配置适当的 worker 数量（通常为 CPU 核心数 * 2 + 1）
   - 启用日志轮转
   - 配置缓存策略

3. **监控告警**
   - 配置健康检查端点监控
   - 设置日志聚合和分析
   - 配置资源使用告警
   - 定期检查服务状态

4. **备份策略**
   - 定期备份配置文件
   - 备份数据库（如使用）
   - 保留多个版本的部署包

## 📚 目录说明

### app/core/
核心配置模块，包含：
- `config.py`: 应用配置类，使用 Pydantic Settings 管理环境变量

### app/routers/
API 路由模块，包含：
- `api.py`: 主路由注册文件，统一管理所有子路由
- `items.py`: 商品相关的 CRUD 操作路由
- `users.py`: 用户相关的 CRUD 操作路由

### app/models/
数据模型模块，用于定义数据库模型（如使用 SQLAlchemy）。

### app/schemas/
Pydantic 模式定义，用于：
- API 请求和响应的数据验证
- 自动生成 API 文档
- 类型安全

### app/services/
业务逻辑服务层，包含：
- 数据处理逻辑
- 业务规则实现
- 与数据库交互的封装
  
包含以下重点服务：
- `ai_service.py`: 使用 DeepSeek 与本地中文向量模型进行菜单意图匹配，内置降级策略
- `menu_service.py`: 调用外部菜单 API，构建第三级菜单名称到 ID 的映射与完整路径映射，带缓存与关键词自动生成
- `permission_service.py`: 菜单权限过滤（占位实现，可对接实际权限中心）

### app/utils/
工具函数模块，包含：
- 日志配置
- 通用工具函数
- 辅助函数

### tests/
测试目录，包含单元测试和集成测试。

## 🔧 配置说明

主要配置项在 `app/core/config.py` 中定义，可通过环境变量覆盖：

- 基础
  - `PROJECT_NAME`: 项目名称
  - `HOST`: 服务器监听地址，默认 `0.0.0.0`
  - `PORT`: 服务器端口，默认 `8001`
  - `DEBUG`: 调试模式
  - `CORS_ORIGINS`: CORS 允许的源
  - `LOG_LEVEL`: 日志级别
  
- AI（DeepSeek）
  - `AI_API_KEY`: API 密钥（务必在生产环境通过环境变量配置）
  - `AI_BASE_URL`: 接口地址，默认 `https://api.deepseek.com`
  - `AI_MODEL`: 模型名，默认 `deepseek-chat`
  
- 菜单 API
  - `MENU_API_BASE_URL`: 菜单服务地址（如 `http://127.0.0.1:8090`）
  - `MENU_API_COOKIE`: 调用菜单服务需要的 Cookie（可为空）
  - `CACHE_TTL`: 菜单缓存 TTL（秒），默认 `3600`
  
- WebSocket
  - `WS_HEARTBEAT_INTERVAL`: 心跳间隔秒数，默认 `30`

## 🧪 运行测试

```bash
pytest
```

或使用详细输出：

```bash
pytest -v
```

## 📝 API 端点

### 基础端点

- `GET /`: 根路径，返回欢迎信息
- `GET /health`: 健康检查端点

### 商品 API

- `GET /api/v1/items/`: 获取商品列表
- `GET /api/v1/items/{item_id}`: 获取单个商品
- `POST /api/v1/items/`: 创建商品
- `PUT /api/v1/items/{item_id}`: 更新商品
- `DELETE /api/v1/items/{item_id}`: 删除商品

### 用户 API
- ### 语音 / 智能导航 API

- `POST /api/v1/voice/command`: 输入文本指令，返回匹配菜单或候选列表；若唯一且有权限，将通过 WebSocket 推送打开指令
- `GET /api/v1/voice/menus`: 用于调试，返回服务端缓存/拉取的菜单列表

- ### WebSocket

- `WS /api/v1/ws/{user_id}`: 建立连接后接收打开菜单等消息
- `GET /api/v1/ws/status/{user_id}`: 查询用户的 WS 连接状态

消息示例（唯一匹配时服务端推送）：

```json
{
  "type": "open_action",
  "menu": "一级-三级名称",
  "user_id": 1,
  "timestamp": "2025-01-01T12:00:00",
  "data": { "type": "open_action", "actionId": 1548 }
}
```

- `GET /api/v1/users/`: 获取用户列表
- `GET /api/v1/users/{user_id}`: 获取单个用户
- `POST /api/v1/users/`: 创建用户
- `PUT /api/v1/users/{user_id}`: 更新用户
- `DELETE /api/v1/users/{user_id}`: 删除用户

## 🛠️ 开发建议

### 代码风格

项目使用 Black 进行代码格式化：

```bash
black .
```

### 类型检查

使用 mypy 进行类型检查：

```bash
mypy app/
```

### 代码检查

使用 flake8 进行代码检查：

```bash
flake8 app/
```

## 📦 扩展功能

### 添加数据库支持

1. 安装数据库相关依赖（取消注释 `requirements.txt` 中的数据库依赖）
2. 在 `app/models/` 中定义数据库模型
3. 在 `app/core/config.py` 中配置数据库连接
4. 在 `app/services/` 中实现数据库操作

### 添加认证功能

1. 安装认证相关依赖（取消注释 `requirements.txt` 中的认证依赖）
2. 在 `app/core/` 中实现 JWT 工具函数
3. 在路由中添加依赖项进行权限验证

### 添加新的 API 端点
### 引入本地中文向量模型（可选）

项目已支持加载本地模型目录 `./bge-small-zh`（如不存在则回退在线 `BAAI/bge-small-zh`）：

1. 将模型目录放置在项目根目录下：`bge-small-zh/`
2. 安装 `sentence-transformers`
3. 服务将自动用向量相似度进行候选排序，失败时降级到关键词匹配


1. 在 `app/schemas/` 中定义请求/响应模式
2. 在 `app/routers/` 中创建新的路由文件
3. 在 `app/services/` 中实现业务逻辑
4. 在 `app/routers/api.py` 中注册新路由

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 Issue 联系。

