# 🚀 FastAPI 分层架构模板

简体中文 | [English](./README_EN.md)

> 一个基于 FastAPI 的生产级后端项目模板，采用**标准分层架构**（Entity / Service / Controller），提供完整的用户认证、异常处理、数据库配置。

![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-00a859?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python)
![License](https://img.shields.io/badge/License-MIT-blue)

## ✨ 核心特性

- ✅ **标准分层架构** — Entity、DTO、Service、Controller 完全分离
- ✅ **用户认证系统** — JWT Token、BCrypt 密码加密、身份验证
- ✅ **RESTful API** — 遵循 REST 规范的完整 CRUD 操作
- ✅ **自动文档** — Swagger UI 和 ReDoc 自动生成
- ✅ **统一响应格式** — 所有返回值统一包装
- ✅ **异常处理** — 全局异常捕获和自定义异常
- ✅ **分页查询** — 完整的分页和列表查询支持
- ✅ **代码生成工具** — 自动生成 CRUD 模块（详见[Code Generator](#-代码生成器)）

## 📦 项目结构

```
Api/
├── main.py                          # FastAPI 入口文件
├── requirements.txt                 # 依赖管理
├── README.md                        # 项目文档
│
├── app/
│   ├── controllers/                 # 控制层（API 路由）
│   │   └── user_controller.py       # 用户控制器
│   │
│   ├── services/                    # 业务逻辑层
│   │   ├── base_service.py          # 基础服务层
│   │   └── user_service.py          # 用户服务
│   │
│   ├── interfaces/                  # 服务接口定义
│   │   ├── ibase_service.py         # 基础服务接口
│   │   └── iuser_service.py         # 用户服务接口
│   │
│   ├── entity/                      # 数据模型层
│   │   ├── base_entity.py           # 基础实体
│   │   └── user_entity.py           # 用户实体 & DTO
│   │
│   └── core/                        # 核心配置和工具
│       ├── config.py                # 配置管理
│       ├── database.py              # 数据库连接和会话
│       ├── exceptions.py            # 异常定义和处理器
│       ├── response.py              # 统一响应格式
│       └── security.py              # 认证和加密工具
│
└── ..
```

## 🚀 快速开始

### 前置要求

- Python 3.10 或更高
- pip 包管理器

### 1️⃣ 克隆仓库

```bash
git clone https://github.com/yourusername/Python_Learn.git
cd Python_Learn/Api
```

### 2️⃣ 安装依赖

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 conda
conda create -n fastapi-env python=3.10
conda activate fastapi-env
pip install -r requirements.txt
```

### 3️⃣ 配置数据库

编辑 `app/core/config.py`，配置数据库 URL：

```python
DATABASE_URL = "sqlite:///./test.db"  # SQLite（开发用）
# 或
DATABASE_URL = "postgresql://user:password@localhost/dbname"  # PostgreSQL
```

### 4️⃣ 启动应用

```bash
# 开发环境（自动重新加载）
uvicorn main:app --reload

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5️⃣ 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API 文档

### 用户相关接口

#### 用户登录
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "user_name": "admin",
  "password": "password123"
}

响应:
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGc...",
    "user": {
      "user_id": 1,
      "user_name": "admin"
    }
  }
}
```

#### 用户注册
```
POST /api/v1/users
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_name": "newuser",
  "password": "password123"
}
```

#### 查询用户
```
GET /api/v1/users/{user_id}
Authorization: Bearer <token>
```

#### 分页查询
```
GET /api/v1/users/page/list?page=1&page_size=10
Authorization: Bearer <token>
```

#### 修改用户
```
PUT /api/v1/users/{user_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_name": "newname"
}
```

#### 删除用户
```
DELETE /api/v1/users/{user_id}
Authorization: Bearer <token>
```

更详细的 API 文档，启动应用后访问 `/docs`

## 🏗️ 分层架构设计

本项目采用标准的**四层分层架构**：

```
┌─────────────────────────────────────────┐
│        客户端 (Client)                   │
└────────────────────┬────────────────────┘
                     │ HTTP 请求
                     ↓
┌─────────────────────────────────────────┐
│     控制层 (Controller/Route)            │ ← user_controller.py
│    • 路由定义                            │
│    • 请求验证                            │
│    • 响应格式化                          │
└────────────────────┬────────────────────┘
                     │ 调用
                     ↓
┌─────────────────────────────────────────┐
│     业务层 (Service)                     │ ← user_service.py
│    • 业务逻辑                            │
│    • 数据验证                            │
│    • 事务处理                            │
└────────────────────┬────────────────────┘
                     │ 操作
                     ↓
┌─────────────────────────────────────────┐
│     数据层 (Entity/ORM)                 │ ← user_entity.py
│    • 数据模型定义                        │
│    • 数据库映射                          │
└────────────────────┬────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────┐
│        数据库 (Database)                 │
│    SQLite / PostgreSQL / MySQL          │
└─────────────────────────────────────────┘
```

### 各层职责

| 层级 | 文件位置 | 职责 | 示例 |
|------|--------|------|------|
| **Controller** | `controllers/` | 定义 API 路由、参数验证 | 接收请求、调用 Service、返回响应 |
| **Service** | `services/` | 实现业务逻辑、数据验证 | 用户注册（检查用户名、密码加密） |
| **Entity** | `entity/` | 定义数据模型、DTO | User 类、UserCreate DTO |
| **Database** | `core/database.py` | 数据库连接、会话管理 | SQLAlchemy 会话、事务 |

## 🔑 核心功能详解

### 1. 用户认证系统

使用 **JWT Token** 和 **BCrypt** 密码加密：

```python
from app.core.security import hash_password, create_access_token, verify_password

# 密码加密
hashed_pwd = hash_password("mypassword")

# 创建 Token
token = create_access_token(user_id=1, user_name="admin")

# 验证密码
is_valid = verify_password("mypassword", hashed_pwd)
```

### 2. 统一响应格式

所有 API 返回值都使用统一格式：

```python
from app.core.response import ResponseModel

# 成功响应
ResponseModel.ok(data=user_data, message="用户查询成功")
# 返回: {"code": 200, "message": "用户查询成功", "data": {...}}

# 错误响应
ResponseModel.fail(code=400, message="参数错误")
# 返回: {"code": 400, "message": "参数错误", "data": null}
```

### 3. 异常处理

全局异常捕获，自动转换为 HTTP 响应：

```python
from app.core.exceptions import AppException, NotFoundException

# 自定义异常
raise AppException("用户已存在", code=400)
raise NotFoundException("用户不存在")
```

### 4. 分页查询

```python
# 查询分页数据
response = service.get_page(page=1, page_size=10)
# 返回: {"total": 100, "pages": 10, "current_page": 1, "items": [...]}
```

## 📖 开发指南

### 新增一个模块（以文章为例）

本项目提供了**自动代码生成工具**，可以一键生成完整的模块代码。

**快速方式：使用代码生成器**

```bash
cd ../代码生成器
python codegen_advanced.py --entity article --output ../Api
```

这会自动生成：
- ✓ `app/entity/article_entity.py` — 数据模型
- ✓ `app/services/article_service.py` — 业务逻辑
- ✓ `app/interfaces/iarticle_service.py` — 服务接口
- ✓ `app/controllers/article_controller.py` — API 路由

**手动方式：完整步骤**

1. 定义实体 (`app/entity/article_entity.py`)：

```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Article(SQLModel, table=True):
    __tablename__ = "articles"
    
    article_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, unique=True, index=True)
    content: str
    author: str = Field(max_length=50)
```

2. 定义 DTO：

```python
class ArticleCreate(SQLModel):
    title: str = Field(max_length=200)
    content: str
    author: str = Field(max_length=50)

class ArticleResponse(SQLModel):
    article_id: int
    title: str
    content: str
    author: str
    
    class Config:
        from_attributes = True
```

3. 创建 Service (`app/services/article_service.py`)：

```python
from app.services.base_service import BaseService
from app.entity.article_entity import Article, ArticleCreate, ArticleUpdate, ArticleResponse

class ArticleService(BaseService[Article, ArticleCreate, ArticleUpdate, ArticleResponse]):
    def __init__(self, session):
        super().__init__(
            session=session,
            entity_class=Article,
            response_class=ArticleResponse,
            pk_field="article_id",
        )
```

4. 创建 Controller (`app/controllers/article_controller.py`)：

```python
from fastapi import APIRouter, Depends
from app.core.database import get_session
from app.services.article_service import ArticleService

router = APIRouter()

def get_article_service(session = Depends(get_session)) -> ArticleService:
    return ArticleService(session)

@router.post("/articles", response_model=ResponseModel[ArticleResponse])
async def create_article(
    dto: ArticleCreate,
    service: ArticleService = Depends(get_article_service),
):
    data = await service.create(dto)
    return ResponseModel.ok(data=data, message="文章创建成功")
```

5. 在 `main.py` 中注册路由：

```python
from app.controllers import article_controller

app.include_router(
    article_controller.router,
    prefix="/api/v1",
    tags=["文章管理"]
)
```

## 🔧 配置管理

编辑 `app/core/config.py` 来配置应用参数：

```python
class Settings:
    APP_NAME = "FastAPI 模板"
    APP_VERSION = "1.0.0"
    DATABASE_URL = "sqlite:///./test.db"
    
    # JWT 配置
    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # CORS 配置
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
```

## 📊 数据库支持

本项目基于 SQLModel，支持多种数据库：

| 数据库 | 连接字符串示例 |
|------|--------------|
| SQLite | `sqlite:///./test.db` |
| PostgreSQL | `postgresql://user:password@localhost/dbname` |
| MySQL | `mysql+pymysql://user:password@localhost/dbname` |
| MariaDB | `mysql+pymysql://user:password@localhost/dbname` |

### 数据库迁移（Alembic）

```bash
# 初始化 Alembic
alembic init migrations

# 自动生成迁移脚本
alembic revision --autogenerate -m "Add user table"

# 应用迁移
alembic upgrade head
```

## 🧪 单元测试

创建测试文件 `tests/test_user_service.py`：

```python
import pytest
from app.services.user_service import UserService
from app.entity.user_entity import UserCreate

@pytest.fixture
def user_service(db_session):
    return UserService(db_session)

def test_create_user(user_service):
    dto = UserCreate(user_name="testuser", password="password123")
    result = user_service.create(dto)
    assert result.user_name == "testuser"
```

运行测试：

```bash
pytest tests/
pytest tests/test_user_service.py -v
```

## 🚀 部署

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
# 构建镜像
docker build -t fastapi-app .

# 运行容器
docker run -p 8000:8000 fastapi-app
```

### 云服务部署

可部署到以下平台：

- **Heroku** — `git push heroku main`
- **AWS EC2** — 使用 Gunicorn + Nginx
- **Railway** — 连接 GitHub 自动部署
- **Render** — 类似 Heroku 的简单部署

## 📖 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLModel 文档](https://sqlmodel.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [JWT 介绍](https://jwt.io/)

## 🛠️ 相关工具

### [代码生成器](../代码生成器/README.md) 

自动生成 CRUD 模块，提高开发效率：

```bash
cd ../代码生成器
python codegen_advanced.py --entity product
python codegen_advanced.py --all
```

详见 [代码生成器文档](../代码生成器/README.md)

## 📝 贡献指南

欢迎提交 Issue 和 Pull Request！

```bash
# 1. Fork 仓库
# 2. 创建特性分支
git checkout -b feature/your-feature

# 3. 提交更改
git commit -am 'Add some feature'

# 4. 推送到分支
git push origin feature/your-feature

# 5. 提交 Pull Request
```

## ❓ FAQ

**Q: 如何添加新的业务字段？**
A: 编辑对应的 Entity 文件，在数据库表中添加字段，然后在 DTO 中定义

**Q: 如何自定义异常处理？**
A: 在 `app/core/exceptions.py` 中定义异常类，然后在 Controller 中使用

**Q: 生产环境用 SQLite 可以吗？**
A: 不推荐。生产环境建议使用 PostgreSQL 或 MySQL

**Q: 如何实现数据库事务？**
A: Service 中的操作自动使用事务，commit 出现异常会自动回滚

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**⭐ 如果这个项目对您有帮助，请给个 Star！**

Made with ❤️ by [Your Name]
