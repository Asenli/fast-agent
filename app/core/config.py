"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    
    # 项目信息
    PROJECT_NAME: str = "FastAPI 服务"
    PROJECT_DESCRIPTION: str = "一个基于 FastAPI 的现代化 Web 服务"
    VERSION: str = "1.0.0"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = True
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 数据库配置（示例）
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # JWT 配置（示例）
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # AI配置 - DeepSeek
    AI_API_KEY: str = "sk-ba87253c34f74a7dbb790fb5776c53eb11"
    AI_BASE_URL: str = "https://api.deepseek.com"
    AI_MODEL: str = "deepseek-chat"
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 菜单缓存TTL（秒）
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # 菜单API配置
    MENU_API_BASE_URL: str = "http://127.0.0.1:8090"
    # MENU_API_BASE_URL: str = "https://jicai-dev.holderzone.cn"
    MENU_API_COOKIE: str = ""  # 完整的 Cookie 字符串，如: frontend_lang=zh_CN; sl-session=...; session_id=...
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

