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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

