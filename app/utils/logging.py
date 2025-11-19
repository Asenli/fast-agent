"""
日志工具模块
"""
import logging
from app.core.config import settings


def setup_logging():
    """配置日志 - 仅使用控制台输出，不保存文件"""
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 仅使用控制台输出
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler()]
    )
    
    return logging.getLogger(__name__)

