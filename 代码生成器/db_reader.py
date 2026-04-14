"""
db_reader.py - 数据库表读取器，支持多种数据库

支持的数据库：MySQL, PostgreSQL, SQL Server, Oracle
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import traceback


@dataclass
class ColumnInfo:
    """列信息"""
    name: str
    type: str
    nullable: bool
    is_primary_key: bool
    comment: str = ""


@dataclass
class TableInfo:
    """表信息"""
    name: str
    comment: str
    columns: List[ColumnInfo]


class DatabaseReader:
    """数据库读取器基类"""
    
    def test_connection(self) -> bool:
        """测试连接"""
        raise NotImplementedError
    
    def get_tables(self) -> List[str]:
        """获取表列表"""
        raise NotImplementedError
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """获取表详细信息"""
        raise NotImplementedError


class MySQLReader(DatabaseReader):
    """MySQL 读取器"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def _get_connection(self):
        """获取连接"""
        try:
            import pymysql
            if self.connection is None:
                self.connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset='utf8mb4'
                )
            return self.connection
        except Exception as e:
            raise Exception(f"MySQL 连接失败: {str(e)}")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """获取表列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{self.database}'")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
        except Exception as e:
            raise Exception(f"获取表列表失败: {str(e)}")
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """获取表详细信息"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 获取列信息
            cursor.execute(f"""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = []
            for row in cursor.fetchall():
                col_name, col_type, nullable, col_key, comment = row
                columns.append(ColumnInfo(
                    name=col_name,
                    type=col_type,
                    nullable=(nullable == 'YES'),
                    is_primary_key=(col_key == 'PRI'),
                    comment=comment or ""
                ))
            
            # 获取表注释
            cursor.execute(f"""
                SELECT TABLE_COMMENT FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{self.database}' AND TABLE_NAME = '{table_name}'
            """)
            table_comment = cursor.fetchone()[0] or ""
            
            cursor.close()
            return TableInfo(name=table_name, comment=table_comment, columns=columns)
        except Exception as e:
            raise Exception(f"获取表信息失败: {str(e)}")


class PostgreSQLReader(DatabaseReader):
    """PostgreSQL 读取器"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def _get_connection(self):
        """获取连接"""
        try:
            import psycopg2
            if self.connection is None:
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            return self.connection
        except Exception as e:
            raise Exception(f"PostgreSQL 连接失败: {str(e)}")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """获取表列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
        except Exception as e:
            raise Exception(f"获取表列表失败: {str(e)}")
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """获取表详细信息"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = []
            for row in cursor.fetchall():
                col_name, col_type, nullable = row
                # 检查是否是主键
                cursor.execute(f"""
                    SELECT tc.constraint_type
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = '{table_name}' AND kcu.column_name = '{col_name}'
                    AND tc.constraint_type = 'PRIMARY KEY'
                """)
                is_pk = cursor.fetchone() is not None
                
                columns.append(ColumnInfo(
                    name=col_name,
                    type=col_type,
                    nullable=(nullable == 'YES'),
                    is_primary_key=is_pk
                ))
            
            cursor.close()
            return TableInfo(name=table_name, comment="", columns=columns)
        except Exception as e:
            raise Exception(f"获取表信息失败: {str(e)}")


class SQLServerReader(DatabaseReader):
    """SQL Server 读取器"""
    
    def __init__(self, server: str, database: str, user: str, password: str, port: int = 1433):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
    
    def _get_connection(self):
        """获取连接"""
        try:
            import pyodbc
            if self.connection is None:
                connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server},{self.port};DATABASE={self.database};UID={self.user};PWD={self.password}'
                self.connection = pyodbc.connect(connection_string)
            return self.connection
        except Exception as e:
            raise Exception(f"SQL Server 连接失败: {str(e)}")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """获取表列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
        except Exception as e:
            raise Exception(f"获取表列表失败: {str(e)}")
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """获取表详细信息"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = []
            for row in cursor.fetchall():
                col_name, col_type, nullable = row
                # 检查是否是主键
                cursor.execute(f"""
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{col_name}'
                    AND CONSTRAINT_NAME LIKE 'PK_%'
                """)
                is_pk = cursor.fetchone() is not None
                
                columns.append(ColumnInfo(
                    name=col_name,
                    type=col_type,
                    nullable=(nullable == 'YES'),
                    is_primary_key=is_pk
                ))
            
            cursor.close()
            return TableInfo(name=table_name, comment="", columns=columns)
        except Exception as e:
            raise Exception(f"获取表信息失败: {str(e)}")


class OracleReader(DatabaseReader):
    """Oracle 读取器"""
    
    def __init__(self, host: str, port: int, user: str, password: str, service_name: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.service_name = service_name
        self.connection = None
    
    def _get_connection(self):
        """获取连接"""
        try:
            import cx_Oracle
            if self.connection is None:
                dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service_name)
                self.connection = cx_Oracle.connect(self.user, self.password, dsn)
            return self.connection
        except Exception as e:
            raise Exception(f"Oracle 连接失败: {str(e)}")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.close()
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """获取表列表"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT table_name FROM user_tables")
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return tables
        except Exception as e:
            raise Exception(f"获取表列表失败: {str(e)}")
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """获取表详细信息"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT column_name, data_type, nullable
                FROM user_tab_columns
                WHERE table_name = upper('{table_name}')
                ORDER BY column_id
            """)
            
            columns = []
            for row in cursor.fetchall():
                col_name, col_type, nullable = row
                # 检查是否是主键
                cursor.execute(f"""
                    SELECT column_name FROM user_cons_columns
                    WHERE table_name = upper('{table_name}')
                    AND column_name = upper('{col_name}')
                    AND constraint_name IN (
                        SELECT constraint_name FROM user_constraints
                        WHERE table_name = upper('{table_name}')
                        AND constraint_type = 'P'
                    )
                """)
                is_pk = cursor.fetchone() is not None
                
                columns.append(ColumnInfo(
                    name=col_name,
                    type=col_type,
                    nullable=(nullable == 'Y'),
                    is_primary_key=is_pk
                ))
            
            cursor.close()
            return TableInfo(name=table_name, comment="", columns=columns)
        except Exception as e:
            raise Exception(f"获取表信息失败: {str(e)}")


def create_reader(db_type: str, **kwargs) -> DatabaseReader:
    """根据数据库类型创建读取器"""
    db_type = db_type.lower()
    
    if db_type == 'mysql':
        return MySQLReader(
            host=kwargs.get('host', 'localhost'),
            port=kwargs.get('port', 3306),
            user=kwargs.get('user', 'root'),
            password=kwargs.get('password', ''),
            database=kwargs.get('database', '')
        )
    elif db_type == 'postgresql':
        return PostgreSQLReader(
            host=kwargs.get('host', 'localhost'),
            port=kwargs.get('port', 5432),
            user=kwargs.get('user', 'postgres'),
            password=kwargs.get('password', ''),
            database=kwargs.get('database', '')
        )
    elif db_type == 'sqlserver':
        return SQLServerReader(
            server=kwargs.get('server', 'localhost'),
            database=kwargs.get('database', ''),
            user=kwargs.get('user', 'sa'),
            password=kwargs.get('password', ''),
            port=kwargs.get('port', 1433)
        )
    elif db_type == 'oracle':
        return OracleReader(
            host=kwargs.get('host', 'localhost'),
            port=kwargs.get('port', 1521),
            user=kwargs.get('user', 'system'),
            password=kwargs.get('password', ''),
            service_name=kwargs.get('service_name', 'ORCL')
        )
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")
