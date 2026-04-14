"""
app/core/db_manager.py — 数据库管理器
提供便捷的读写分离管理接口
"""
from sqlmodel import Session
from app.core.database import (
    DatabaseType,
    get_session,
    engine_write,
    engine_read,
    engine_other,
)


class DBManager:
    """数据库管理器 - 简化读写分离操作"""
    
    @staticmethod
    def get_write_session() -> Session:
        """获取写库 Session"""
        return get_session(DatabaseType.WRITE)
    
    @staticmethod
    def get_read_session() -> Session:
        """获取读库 Session"""
        return get_session(DatabaseType.READ)
    
    @staticmethod
    def get_other_session() -> Session:
        """获取其他库 Session"""
        return get_session(DatabaseType.OTHER)
    
    @staticmethod
    def get_session(db_type: DatabaseType = DatabaseType.WRITE) -> Session:
        """获取指定类型的 Session"""
        return get_session(db_type)
    
    @staticmethod
    def execute_write(sql: str, params: dict = None):
        """直接在写库执行 SQL（用于复杂的 SQL 语句）"""
        session = DBManager.get_write_session()
        try:
            result = session.exec(sql, params or {})
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def execute_read(sql: str, params: dict = None):
        """直接在读库执行 SQL（用于复杂的 SELECT 查询）"""
        session = DBManager.get_read_session()
        try:
            result = session.exec(sql, params or {})
            return result
        finally:
            session.close()
    
    @staticmethod
    def execute_other(sql: str, params: dict = None):
        """直接在其他库执行 SQL"""
        session = DBManager.get_other_session()
        try:
            result = session.exec(sql, params or {})
            return result
        finally:
            session.close()


# 便捷函数
def db_write() -> Session:
    """快捷函数：获取写库 Session"""
    return DBManager.get_write_session()


def db_read() -> Session:
    """快捷函数：获取读库 Session"""
    return DBManager.get_read_session()


def db_other() -> Session:
    """快捷函数：获取其他库 Session"""
    return DBManager.get_other_session()
