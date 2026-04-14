# 📖 数据库优化 - 快速参考卡

## 🎯 核心改进概览

您的 API 项目已完成以下优化：

```
┌─────────────────────────────────────────────────────┐
│  ✅ 实现了读写分离                                   │
│     - 主库（写）：负责所有写操作                    │
│     - 从库（读）：负责所有读操作                    │
│     - 性能提升：减轻主库压力，并发查询速度更快      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  ✅ 支持多数据库连接                                │
│     - 主库连接：应用主数据库                        │
│     - 从库连接：只读从库（可选）                    │
│     - 其他库连接：分析库/日志库/第三方库            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  ✅ 完整的示例代码                                   │
│     - Service 层实现示例                            │
│     - Controller 层实现示例                         │
│     - 应用启动示例                                  │
└─────────────────────────────────────────────────────┘
```

---

## 📂 生成的文件一览

| 文件 | 类型 | 说明 |
|------|------|------|
| **core/config.py** | ✏️ 更新 | 添加了三个数据库配置 |
| **core/database.py** | ✏️ 重写 | 完全支持读写分离 |
| **core/db_manager.py** | ✨ 新建 | 数据库管理器工具类 |
| **DATABASE_OPTIMIZATION_GUIDE.md** | 📖 新建 | **详细使用指南** |
| **OPTIMIZATION_SUMMARY.md** | 📖 新建 | **优化总结** |
| **services/user_service_example.py** | 📖 新建 | Service 实现参考 |
| **controllers/user_controller_example.py** | 📖 新建 | Controller 实现参考 |
| **main_example.py** | 📖 新建 | 应用启动参考 |

---

## 🚀 立即开始（5 分钟）

### 1️⃣ 配置数据库 (1 分钟)

编辑 `app/core/config.py`：

```python
# 主库（写库）
DATABASE_WRITE_URL = "mysql+pymysql://root:pass@localhost:3306/mydb"

# 从库（读库）
DATABASE_READ_URL = "mysql+pymysql://readonly:pass@slave:3306/mydb"

# 其他库
DATABASE_OTHER_URL = "mysql+pymysql://root:pass@localhost:3306/analytics"
```

### 2️⃣ 测试连接 (1 分钟)

在 `main.py` 中添加启动测试：

```python
from app.core.database import test_connection, create_db_and_tables

@app.on_event("startup")
async def startup():
    all_ok, results = test_connection()
    if not all_ok:
        print("❌ 某些库连接失败:", results)
    create_db_and_tables()
```

### 3️⃣ 使用读写分离 (3 分钟)

在控制器中：

```python
from app.core.database import get_session_read, get_session_write

# 读操作
@app.get("/users")
def list_users(session: Session = Depends(get_session_read)):
    return session.query(User).all()

# 写操作
@app.post("/users")
def create_user(session: Session = Depends(get_session_write)):
    user = User(name="John")
    session.add(user)
    session.commit()
    return user
```

---

## 💻 常用函数速查

### 导入

```python
from app.core.database import (
    get_session_read,      # 获取读库 Session
    get_session_write,     # 获取写库 Session
    get_session_other,     # 获取其他库 Session
    test_connection,       # 测试连接
    create_db_and_tables,  # 初始化表
)

from app.core.db_manager import (
    DBManager,             # 数据库管理器
    db_read, db_write,     # 快捷函数
)
```

### FastAPI 依赖注入

```python
# 获取读库
session_read: Session = Depends(get_session_read)

# 获取写库
session_write: Session = Depends(get_session_write)

# 获取其他库
session_other: Session = Depends(get_session_other)
```

### 直接使用

```python
# 方式 A：直接获取 Session
from app.core.database import get_session, DatabaseType
session = get_session(DatabaseType.READ)

# 方式 B：使用管理器
from app.core.db_manager import DBManager
session = DBManager.get_read_session()

# 方式 C：使用便捷函数
from app.core.db_manager import db_read, db_write
session_read = db_read()
session_write = db_write()
```

---

## 📊 读写分离路由设计规范

```python
✅ 正确做法                              ❌ 错误做法
─────────────────────────────────────────────────────

GET /users                               GET /users
  → 使用 get_session_read()                → 使用 get_session_write()

POST /users                              POST /users  
  → 使用 get_session_write()               → 使用 get_session_read()

PUT /users/{id}                          PUT /users/{id}
  → 使用 get_session_write()               → 使用 get_session_read()

DELETE /users/{id}                       DELETE /users/{id}
  → 使用 get_session_write()               → 使用 get_session_read()

GET /users/{id}                          GET /users/{id}
  → 使用 get_session_read()                → 使用 get_session_write()
```

---

## 🔄 Service 层升级模板

### 旧版本（单库）

```python
class UserService:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, data): ...
    def get(self, id): ...
```

### 新版本（读写分离）

```python
class UserService:
    def __init__(self, session_write: Session, session_read: Session):
        self.session_write = session_write  # INSERT/UPDATE/DELETE
        self.session_read = session_read    # SELECT
    
    def create(self, data):
        # 使用 self.session_write
        ...
    
    def get(self, id):
        # 使用 self.session_read
        ...
```

---

## ⚠️ 常见陷阱

| 陷阱 | 症状 | 解决 |
|------|------|------|
| 创建后立即查询为空 | 数据创建成功但查询不到 | 改用写库查询最新数据 |
| 事务提交失败 | 数据保存不成功 | 确保使用的是写库 Session |
| 连接超时 | "Lost connection to MySQL" | 检查 pool_recycle 配置 |
| 从库延迟 | 查询不到最新数据 | 参考"延迟处理"部分 |

---

## 🎓 延迟处理最佳实践

### 场景 1：创建即返回

```python
# ❌ 错误
@app.post("/users")
def create(data: UserCreate, s_write = Depends(get_session_write), 
           s_read = Depends(get_session_read)):
    user = create_user(data, s_write)
    return get_user(user.id, s_read)  # 可能查不到

# ✅ 正确
@app.post("/users")
def create(data: UserCreate, s_write = Depends(get_session_write)):
    user = create_user(data, s_write)
    s_write.refresh(user)  # 从写库刷新
    return user
```

### 场景 2：级联操作

```python
# ✅ 推荐：多个写操作必须用写库
def complex_operation(s_write = Depends(get_session_write)):
    user = create_user(data, s_write)
    profile = create_profile(user.id, s_write)  # 用同一个写库
    return (user, profile)
```

---

## 📞 快速故障排查

### 问题：应用启动时报"无法连接读库"

```
❌ 症状：
  数据库连接失败: 无法连接到 localhost:3306

✅ 解决方案：
  1. 检查 config.py 中 DATABASE_READ_URL 是否正确
  2. 确保数据库服务正在运行
  3. 检查防火墙是否限制了连接
  4. 如果没有从库，将 DATABASE_READ_URL 设为与 DATABASE_WRITE_URL 相同
```

### 问题：创建用户后查询返回空

```
❌ 症状：
  POST /users 返回 {"id": 1, "name": "John"}
  GET /users/1 返回 null 或 404

✅ 解决方案：
  1. 这是正常的读库延迟（1-5秒）
  2. 改为在写库上查询：session_write.get(User, user_id)
  3. 或者等待后再查询
```

### 问题：update 操作后看不到最新数据

```
❌ 症状：
  PUT /users/1 更新成功，但 GET /users/1 看不到新数据

✅ 解决方案：
  确保在同一个写库 Session 上刷新数据：
  session_write.refresh(user)
```

---

## 📚 详细文档

- **完整指南** → 看 `DATABASE_OPTIMIZATION_GUIDE.md`
- **优化总结** → 看 `OPTIMIZATION_SUMMARY.md`
- **实现参考** → 看 `*_example.py` 文件

---

## ✨ 性能提升预期

| 指标 | 改进 |
|------|------|
| 读并发能力 | ⬆️ 3-5 倍（取决于从库配置） |
| 写操作延迟 | ➡️ 无变化（主库单点） |
| 主库负载 | ⬇️ 30-50%（读操作全部转到从库） |
| 系统可扩展性 | ⬆️ 显著提升（从库可动态扩展） |

---

## 🎯 下一步

- [ ] 更新 `config.py` 数据库配置
- [ ] 在 `main.py` 添加启动测试
- [ ] 参考示例文件升级 Service 层
- [ ] 参考示例文件升级 Controller 层
- [ ] 本地测试验证
- [ ] 部署到测试环境
- [ ] 部署到生产环境

---

**提示**：遇到问题？查看 `DATABASE_OPTIMIZATION_GUIDE.md` 的"常见问题"部分！
