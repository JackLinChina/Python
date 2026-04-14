"""
app/core/config.py — 全局配置
支持读写分离和多数据库连接
"""
from pydantic_settings import BaseSettings
from typing import List

# ===== 主数据库配置（写库）=====
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB = "test"

DATABASE_WRITE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# ===== 从数据库配置（读库）=====
# 可选配置，若为空则使用主库
MYSQL_READ_HOST = "localhost"  # 读库地址（可指向另一个MySQL实例或同一实例的不同端口）
MYSQL_READ_PORT = "3306"
MYSQL_READ_USER = "root"  # 建议使用只读账户
MYSQL_READ_PASSWORD = "123456"

DATABASE_READ_URL = f"mysql+pymysql://{MYSQL_READ_USER}:{MYSQL_READ_PASSWORD}@{MYSQL_READ_HOST}:{MYSQL_READ_PORT}/{MYSQL_DB}"

# ===== 其他数据库配置（如分析库、日志库等）=====
OTHER_DB_NAME = "test2"  # 其他数据库名称
OTHER_DB_USER = "root"
OTHER_DB_PASSWORD = "123456"
OTHER_DB_HOST = "localhost"
OTHER_DB_PORT = "3306"

DATABASE_OTHER_URL = f"mysql+pymysql://{OTHER_DB_USER}:{OTHER_DB_PASSWORD}@{OTHER_DB_HOST}:{OTHER_DB_PORT}/{OTHER_DB_NAME}"


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI 分层架构"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_WRITE_URL: str = DATABASE_WRITE_URL  # 写库
    DATABASE_READ_URL: str = DATABASE_READ_URL    # 读库
    DATABASE_OTHER_URL: str = DATABASE_OTHER_URL  # 其他库
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # JWT 配置
    JWT_SECRET_KEY: str = "change-this-secret-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 默认 24 小时

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()