"""
app/core/config.py — 全局配置
"""
from pydantic_settings import BaseSettings
from typing import List

# MySQL 配置
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB = "test"

# 构建 DATABASE_URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI 分层架构"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = DATABASE_URL  # ✅ 添加类型注解 : str
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # JWT 配置
    JWT_SECRET_KEY: str = "change-this-secret-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 默认 24 小时

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()