"""
app/core/database.py — 数据库连接 & Session 依赖注入
支持读写分离和多数据库连接
"""
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import text
from app.core.config import settings
from enum import Enum

class DatabaseType(Enum):
    """数据库类型枚举"""
    WRITE = "write"      # 主数据库（写操作）
    READ = "read"        # 从数据库（读操作）
    OTHER = "other"      # 其他数据库


def _create_engine(database_url: str, engine_name: str = "default"):
    """
    通用的引擎创建函数
    
    Args:
        database_url: 数据库连接字符串
        engine_name: 引擎名称（用于日志）
    
    Returns:
        SQLAlchemy Engine
    """
    if "sqlite" in database_url:
        # SQLite 配置
        return create_engine(
            database_url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )
    else:
        # MySQL 优化配置
        return create_engine(
            database_url,
            echo=settings.DEBUG,           # 是否打印SQL语句（开发环境True）
            pool_size=10,                  # 连接池大小
            max_overflow=20,               # 最大溢出连接数
            pool_pre_ping=True,            # 使用前检查连接是否有效
            pool_recycle=3600,             # 连接回收时间（秒），避免MySQL 8小时超时
            pool_timeout=30,               # 获取连接超时时间
        )


# ===== 创建三个数据库引擎 =====
# 写引擎（主数据库）- 用于 INSERT/UPDATE/DELETE
engine_write = _create_engine(settings.DATABASE_WRITE_URL, "Write")

# 读引擎（从数据库）- 用于 SELECT
engine_read = _create_engine(settings.DATABASE_READ_URL, "Read")

# 其他数据库引擎
engine_other = _create_engine(settings.DATABASE_OTHER_URL, "Other")


def create_db_and_tables():
    """初始化数据库表（应用启动时调用）
    
    说明：
    - 只在主库（写库）上创建表结构
    - 从库通过主从同步自动获得表结构
    - 建表前禁用外键检查，建表后启用（避免外键约束错误）
    """
    try:
        with engine_write.connect() as connection:
            # 禁用外键检查
            connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            connection.commit()
        
        # 创建所有表
        SQLModel.metadata.create_all(engine_write)
        
        # 启用外键检查
        with engine_write.connect() as connection:
            connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            connection.commit()
        
        print("✅ 数据库表初始化完成（主库）")
    except Exception as e:
        print(f"❌ 数据库表初始化失败: {e}")
        print("💡 建议：")
        print("   1. 检查数据库连接是否正常")
        print("   2. 检查数据库是否已创建")
        print("   3. 如果表已存在，可以注释掉 create_db_and_tables() 的调用")
        raise


def get_session_write() -> Session:
    """FastAPI 依赖注入：提供写入数据库 Session
    
    用于：INSERT / UPDATE / DELETE 操作
    
    Usage:
        @app.post("/users")
        def create_user(session: Session = Depends(get_session_write)):
            ...
    """
    with Session(engine_write) as session:
        yield session


def get_session_read() -> Session:
    """FastAPI 依赖注入：提供读取数据库 Session（读库）
    
    用于：SELECT 操作
    建议：用于分页、查询大量数据等读取操作
    
    Usage:
        @app.get("/users")
        def list_users(session: Session = Depends(get_session_read)):
            ...
    """
    with Session(engine_read) as session:
        yield session


def get_session_other() -> Session:
    """FastAPI 依赖注入：提供其他数据库 Session
    
    用于：访问其他数据库（如分析库、日志库）
    
    Usage:
        @app.get("/analytics")
        def get_analytics(session: Session = Depends(get_session_other)):
            ...
    """
    with Session(engine_other) as session:
        yield session


def get_session(db_type: DatabaseType = DatabaseType.WRITE) -> Session:
    """通用的 Session 获取函数
    
    Args:
        db_type: 数据库类型（WRITE/READ/OTHER）
    
    Returns:
        所对应的数据库 Session
    
    Usage:
        session = get_session(DatabaseType.READ)
        # 或
        session = get_session(DatabaseType.WRITE)
    """
    if db_type == DatabaseType.WRITE:
        return Session(engine_write)
    elif db_type == DatabaseType.READ:
        return Session(engine_read)
    elif db_type == DatabaseType.OTHER:
        return Session(engine_other)
    else:
        raise ValueError(f"未知的数据库类型: {db_type}")


def test_connection():
    """测试所有数据库连接"""
    results = {
        "write": False,
        "read": False,
        "other": False,
    }
    
    try:
        with Session(engine_write) as session:
            session.exec(text("SELECT 1"))
            print("✅ 写库连接成功")
            results["write"] = True
    except Exception as e:
        print(f"❌ 写库连接失败: {e}")
    
    try:
        with Session(engine_read) as session:
            session.exec(text("SELECT 1"))
            print("✅ 读库连接成功")
            results["read"] = True
    except Exception as e:
        print(f"❌ 读库连接失败: {e}")
    
    try:
        with Session(engine_other) as session:
            session.exec(text("SELECT 1"))
            print("✅ 其他库连接成功")
            results["other"] = True
    except Exception as e:
        print(f"❌ 其他库连接失败: {e}")
    
    return all(results.values()), results