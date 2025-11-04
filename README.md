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
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

启动服务后，访问以下地址：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API 根路径: http://localhost:8000/

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

### app/utils/
工具函数模块，包含：
- 日志配置
- 通用工具函数
- 辅助函数

### tests/
测试目录，包含单元测试和集成测试。

## 🔧 配置说明

主要配置项在 `app/core/config.py` 中定义，可通过环境变量覆盖：

- `PROJECT_NAME`: 项目名称
- `HOST`: 服务器监听地址
- `PORT`: 服务器端口
- `DEBUG`: 调试模式
- `CORS_ORIGINS`: CORS 允许的源
- `DATABASE_URL`: 数据库连接 URL
- `SECRET_KEY`: JWT 密钥
- `LOG_LEVEL`: 日志级别

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

