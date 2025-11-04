"""
日志工具模块
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """配置日志"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        datefmt=date_format,
        handlers=[
            RotatingFileHandler(
                log_dir / "app.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

