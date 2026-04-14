"""
app/core/database.py — 数据库连接 & Session 依赖注入
"""
from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings

# 数据库引擎配置
if "sqlite" in settings.DATABASE_URL:
    # SQLite 配置
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )
else:
    # MySQL 优化配置
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,           # 是否打印SQL语句（开发环境True）
        pool_size=10,                  # 连接池大小
        max_overflow=20,               # 最大溢出连接数
        pool_pre_ping=True,            # 使用前检查连接是否有效
        pool_recycle=3600,             # 连接回收时间（秒），避免MySQL 8小时超时
        pool_timeout=30,               # 获取连接超时时间
    )

def create_db_and_tables():
    """初始化数据库表（应用启动时调用）"""
    SQLModel.metadata.create_all(engine)
    print("✅ 数据库表初始化完成")

def get_session():
    """FastAPI 依赖注入：提供数据库 Session"""
    with Session(engine) as session:
        yield session

# 可选：测试连接
def test_connection():
    """测试数据库连接"""
    try:
        with Session(engine) as session:
            session.execute("SELECT 1")
            print("✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False