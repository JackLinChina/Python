# 数据库读写分离与多库连接使用指南

## 📋 概述

本项目已升级为支持：
1. **读写分离** - 主库用于写操作（写库），从库用于读操作（读库）
2. **多数据库连接** - 支持连接第三个数据库（如分析库、日志库等）

---

## 🔧 配置说明

在 `app/core/config.py` 中配置三个数据库连接：

```python
# 写库（主库）- 用于 INSERT/UPDATE/DELETE
DATABASE_WRITE_URL = "mysql+pymysql://root:123456@localhost:3306/test"

# 读库（从库）- 用于 SELECT
DATABASE_READ_URL = "mysql+pymysql://readonly_user:readonly_pass@localhost:3306/test"

# 其他库（如分析库）- 用于读取其他数据库
DATABASE_OTHER_URL = "mysql+pymysql://root:123456@localhost:3306/analytics"
```

> **注意**：
> - 如果没有读库，可将 `DATABASE_READ_URL` 设置为与写库相同的地址
> - 建议为读库配置专用的只读数据库账户以提高安全性

---

## 📚 使用方式

### 1. 在 FastAPI 控制器中使用

#### 方式 A：使用依赖注入（推荐）

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session_read, get_session_write
from app.entity.user_entity import User

router = APIRouter()

# 读操作 - 使用读库
@router.get("/users")
def list_users(session: Session = Depends(get_session_read)):
    """从读库查询用户"""
    users = session.query(User).all()
    return users

# 写操作 - 使用写库
@router.post("/users")
def create_user(name: str, session: Session = Depends(get_session_write)):
    """向写库创建用户"""
    user = User(name=name)
    session.add(user)
    session.commit()
    return user

# 其他库操作
@router.get("/analytics")
def get_analytics(session: Session = Depends(get_session_other)):
    """从分析库读取数据"""
    # 执行分析库查询
    pass
```

#### 方式 B：使用 DBManager 管理器

```python
from app.core.db_manager import DBManager, db_read, db_write
from app.entity.user_entity import User

# 方式 1：使用管理器方法
def list_users():
    session = DBManager.get_read_session()
    users = session.query(User).all()
    session.close()
    return users

# 方式 2：使用便捷函数
def create_user(name: str):
    session = db_write()
    user = User(name=name)
    session.add(user)
    session.commit()
    session.close()
    return user
```

---

### 2. 在 Service 层中使用

修改 `base_service.py` 支持读写分离：

```python
from typing import Generic, TypeVar, Optional, List, Type
from sqlmodel import Session, select
from app.core.database import DatabaseType, get_session

class BaseService(IBaseService[EntityT, CreateT, UpdateT, ResponseT]):
    
    def __init__(
        self,
        session_write: Session,  # 写库 Session
        session_read: Session,   # 读库 Session
        entity_class: Type[EntityT],
        response_class: Type[ResponseT],
        pk_field: str = "id",
    ):
        self.session_write = session_write  # 用于 INSERT/UPDATE/DELETE
        self.session_read = session_read    # 用于 SELECT
        self.entity_class = entity_class
        self.response_class = response_class
        self.pk_field = pk_field

    def list_all(self, skip: int = 0, limit: int = 10) -> List[ResponseT]:
        """从读库查询数据"""
        entities = self.session_read.exec(
            select(self.entity_class).offset(skip).limit(limit)
        ).all()
        return [self.response_class.from_orm(e) for e in entities]

    def create(self, entity_data: CreateT) -> ResponseT:
        """向写库创建数据"""
        entity = self.entity_class(**entity_data.dict())
        self.session_write.add(entity)
        self.session_write.commit()
        self.session_write.refresh(entity)
        return self.response_class.from_orm(entity)

    def update(self, entity_id: int, entity_data: UpdateT) -> ResponseT:
        """向写库更新数据"""
        entity = self.session_write.get(self.entity_class, entity_id)
        for key, value in entity_data.dict(exclude_unset=True).items():
            setattr(entity, key, value)
        self.session_write.add(entity)
        self.session_write.commit()
        self.session_write.refresh(entity)
        return self.response_class.from_orm(entity)

    def delete(self, entity_id: int) -> bool:
        """从写库删除数据"""
        entity = self.session_write.get(self.entity_class, entity_id)
        self.session_write.delete(entity)
        self.session_write.commit()
        return True
```

---

### 3. 在控制器中创建 Service 实例

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session_read, get_session_write
from app.services.user_service import UserService

router = APIRouter()

@router.get("/users")
def list_users(
    session_read: Session = Depends(get_session_read),
    session_write: Session = Depends(get_session_write),
):
    """列表用户"""
    service = UserService(
        session_write=session_write,
        session_read=session_read,
    )
    return service.list_all()

@router.post("/users")
def create_user(
    name: str,
    session_write: Session = Depends(get_session_write),
    session_read: Session = Depends(get_session_read),
):
    """创建用户"""
    service = UserService(
        session_write=session_write,
        session_read=session_read,
    )
    return service.create(name)
```

---

## 🎯 使用场景

| 场景 | 使用的库 | 说明 |
|------|--------|------|
| 用户注册、数据修改、订单提交 | **写库** | 使用主库以确保数据一致性 |
| 用户查询、数据统计、列表展示 | **读库** | 使用从库，减轻主库压力 |
| 分析报表、日志查询、BI 操作 | **其他库** | 读取专用的分析/日志库 |

---

## 🔍 测试数据库连接

在应用启动时测试所有数据库连接：

```python
from fastapi import FastAPI
from app.core.database import test_connection, create_db_and_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # 测试数据库连接
    all_ok, results = test_connection()
    if not all_ok:
        print("⚠️ 某些数据库连接失败，请检查配置")
        for db, ok in results.items():
            print(f"  {db}: {'✅' if ok else '❌'}")
    
    # 初始化数据库表
    create_db_and_tables()
```

---

## ⚠️ 常见问题

### Q1: 如何处理读库延迟？
**A**: 读库可能存在与主库的数据延迟（1-5 秒），对于需要最新数据的操作，应该使用写库查询。

```python
# 创建后立即查询 - 使用写库
user = service.create(user_data)
user_detail = session_write.get(User, user.id)
```

### Q2: 如果没有专用读库怎么办？
**A**: 在 `config.py` 中将 `DATABASE_READ_URL` 设置为与 `DATABASE_WRITE_URL` 相同即可。

### Q3: 如何添加第四个数据库连接？
**A**: 参考 `database.py` 中的模式，添加新的引擎和 Session 获取函数：

```python
DATABASE_CACHE_URL = "redis://localhost:6379/0"
engine_cache = _create_engine(DATABASE_CACHE_URL, "Cache")

def get_session_cache() -> Session:
    with Session(engine_cache) as session:
        yield session
```

---

## 📦 依赖包

确保已安装必要的依赖：

```bash
pip install sqlmodel
pip install pymysql
pip install fastapi
```

---

## 🚀 迁移建议

1. **第一步**：更新 `config.py`，配置读写库地址
2. **第二步**：重新启动应用，验证所有库连接
3. **第三步**：逐步更新 Service 层，分离读写操作
4. **第四步**：更新控制器，使用新的 Session 注入方式

---

