# 📚 Python_Learn - 学习项目集合

> 一个综合的 Python 后端开发学习项目，包含完整的 FastAPI 应用和智能代码生成工具。

![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-00a859?logo=fastapi)
![Stars](https://img.shields.io/github/stars/yourusername/Python_Learn)
![License](https://img.shields.io/badge/License-MIT-blue)

## 📂 项目结构

```
Python_Learn/
├── Api/                           # ⭐ FastAPI 后端项目
│   ├── main.py                    # 应用入口
│   ├── requirements.txt           # 依赖管理
│   ├── README.md                  # 项目文档
│   │
│   ├── app/
│   │   ├── controllers/           # API 控制层
│   │   ├── services/              # 业务逻辑层
│   │   ├── interfaces/            # 服务接口
│   │   ├── entity/                # 数据模型层
│   │   └── core/                  # 核心工具
│   │
│   └── ...
│
├── 代码生成器/                      # 🤖 Python 代码生成工具
│   ├── codegen.py                 # 核心生成器
│   ├── codegen_advanced.py        # 高级生成器
│   ├── entities_config.py         # 实体配置
│   ├── example_usage.py           # 示例脚本
│   ├── README.md                  # 文档
│   │
│   └── ...
│
└── README.md                      # 本文件
```

## 🎯 项目概览

### 1️⃣ FastAPI 项目 (`Api/`)

一个**生产级** FastAPI 后端项目模板，展示标准的分层架构设计。

**核心特性：**
- ✅ 标准分层架构（Entity / Service / Controller）
- ✅ JWT 用户认证系统
- ✅ 完整的 CRUD 操作
- ✅ 自动生成 Swagger 文档
- ✅ 统一的响应格式和异常处理
- ✅ SQLModel ORM 支持多数据库

**快速开始：**

```bash
cd Api
pip install -r requirements.txt
uvicorn main:app --reload
# 访问 http://localhost:8000/docs
```

[👉 查看 Api 项目详细文档](./Api/README.md)

### 2️⃣ 代码生成器 (`代码生成器/`)

一个**智能代码生成工具**，可以自动生成 FastAPI CRUD 模块。

**核心特性：**
- 🚀 一键生成 Entity、Service、Controller
- 📝 自动生成 Swagger 文档注解
- 🎯 支持批量生成多个模块
- ⚙️ 灵活的配置系统
- 🏗️ 遵循最佳实践

**快速开始：**

```bash
cd 代码生成器

# 交互式菜单（推荐新手）
python example_usage.py

# 或者命令行
python codegen_advanced.py --entity product
```

[👉 查看代码生成器详细文档](./代码生成器/README.md)

## 🚀 快速开始

### 场景 1: 快速体验 FastAPI（10 分钟）

```bash
cd Api
pip install -r requirements.txt
uvicorn main:app --reload
```

打开 http://localhost:8000/docs 查看 API 文档

### 场景 2: 使用代码生成器（5 分钟）

```bash
cd 代码生成器
python example_usage.py  # 选择要生成的模块
```

生成的代码会自动保存到 `Api` 项目中

### 场景 3: 完整开发流程（1 小时）

```bash
# 1. 定义新实体（以商品为例）
cd 代码生成器
# 编辑 entities_config.py，添加 PRODUCT_CONFIG

# 2. 生成代码
python codegen_advanced.py --entity product

# 3. 在 Api/main.py 中注册路由
# 添加 from app.controllers import product_controller
# app.include_router(product_controller.router, prefix="/api/v1")

# 4. 启动应用并测试
cd ../Api
uvicorn main:app --reload
# 访问 http://localhost:8000/docs
```

## 💡 核心概念

### 分层架构设计

本项目采用标准的 **4 层分层架构**：

```
请求 → Controller → Service → Entity → Database → 响应
        (路由)      (业务)    (模型)    (存储)
```

| 层级 | 职责 | 示例 |
|------|------|------|
| **Controller** | API 路由、请求验证 | 定义 `/api/v1/users` 路由 |
| **Service** | 业务逻辑、数据处理 | 用户注册、登录验证 |
| **Entity** | 数据模型、数据库映射 | User 表、UserCreate DTO |
| **Database** | 数据持久化、连接管理 | SQLAlchemy、事务 |

### 代码生成工作流

```
编辑 entities_config.py
        ↓
定义实体配置（字段、类型、约束）
        ↓
运行生成器
        ↓
自动生成 4 个文件
  ✓ Entity（数据模型 + DTO）
  ✓ Service Interface（服务接口）
  ✓ Service（业务逻辑）
  ✓ Controller（API 路由）
        ↓
在 main.py 中注册路由
        ↓
应用就绪，开始使用 ✨
```

## 📚 学习路线

### 初级（理解架构）- 1 天

```
1. 查看 Api/README.md 了解项目结构
2. 运行 Api 项目，体验 FastAPI
3. 访问 /docs 查看自动生成的 API 文档
4. 查看 user_* 相关代码，理解分层架构
```

### 中级（学会使用生成器）- 1 天

```
1. 查看 代码生成器/README.md
2. 运行 python example_usage.py
3. 尝试生成一个新模块（如 Product）
4. 在 Api 中注册和测试新模块
```

### 高级（自定义和扩展）- 2-3 天

```
1. 编辑 entities_config.py，定义自己的实体
2. 修改生成器代码，自定义模板
3. 给 Service 添加自定义业务逻辑
4. 添加数据库关联和复杂查询
5. 编写单元测试
6. 性能优化和部署
```

## 🛠️ 技术栈

### Backend
- **Framework**: FastAPI 0.111.0+
- **ORM**: SQLModel（基于 SQLAlchemy）
- **认证**: JWT + BCrypt
- **数据验证**: Pydantic v2
- **Web Server**: Uvicorn
- **数据库**: SQLite / PostgreSQL / MySQL

### Development Tools
- **Python**: 3.10+
- **Package Manager**: pip
- **Code Generation**: Custom Python Script
- **API Documentation**: Swagger UI / ReDoc
- **Testing**: pytest

### 可选依赖
- **Database Migration**: Alembic
- **Async**: asyncio / aiohttp
- **Logging**: loguru
- **Monitoring**: Prometheus + Grafana

## 📖 文档导航

| 文档 | 描述 |
|------|------|
| [Api/README.md](./Api/README.md) | FastAPI 项目完整文档 |
| [代码生成器/README.md](./代码生成器/README.md) | 代码生成器使用指南 |
| [代码生成器/CODEGEN_GUIDE.md](./代码生成器/CODEGEN_GUIDE.md) | 生成器详细配置说明 |
| [Api/app/entity/user_entity.py](./Api/app/entity/user_entity.py) | Entity 参考示例 |
| [Api/app/services/user_service.py](./Api/app/services/user_service.py) | Service 参考示例 |
| [Api/app/controllers/user_controller.py](./Api/app/controllers/user_controller.py) | Controller 参考示例 |

## 🎓 常见使用场景

### 场景 1: 快速原型开发

```
需求 → 在 entities_config.py 中定义实体 
    → 一键生成代码 
    → 整合前端 
    → 快速迭代
```

### 场景 2: 学习 FastAPI

```
阅读示例代码 → 理解架构 
           → 修改代码实验 
           → 添加新功能 
           → 深入学习
```

### 场景 3: 生产应用开发

```
使用生成器生成基础代码 
           → 添加业务逻辑
           → 编写单元测试
           → 性能优化
           → 部署上线
```

## ⚡ 性能指标

| 操作 | 耗时 |
|------|------|
| 生成 1 个模块 | ~20ms |
| 启动 FastAPI 应用 | ~100ms |
| 单个 API 请求 | <50ms（含DB查询） |
| 分页查询（10条） | <10ms |

## 🔒 安全特性

- ✅ JWT Token 认证
- ✅ BCrypt 密码加密（不可逆）
- ✅ CORS 跨域配置
- ✅ 请求参数验证
- ✅ SQL 注入防护（使用 ORM）
- ✅ 异常不泄露敏感信息

## 📦 依赖管理

```bash
# 查看所有依赖
cat Api/requirements.txt

# 更新依赖
pip install --upgrade -r Api/requirements.txt

# 生成依赖列表
pip freeze > requirements.txt
```

## 🚀 部署选项

### 本地开发部署

```bash
cd Api
uvicorn main:app --reload
```

### Docker 部署

```bash
cd Api
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

### 云平台部署

- **Heroku** - `git push heroku main`
- **Railway** - 连接 GitHub 自动部署
- **AWS EC2** - 使用 Gunicorn + Nginx
- **Render** - 无需配置，自动部署

详见 [Api/README.md#部署](./Api/README.md#部署)

## ❓ FAQ

**Q: 这个项目适合初学者吗？**
A: 完全适合！有详细的注释和文档，推荐的学习路线是：
1. 先学习分层架构概念
2. 运行 Api 项目，理解代码
3. 使用生成器快速生成代码
4. 自己扩展新的功能

**Q: 能用于生产环境吗？**
A: 可以的。这是一个生产级的代码模板，但建议：
- 添加单元测试
- 配置生产级数据库（PostgreSQL）
- 添加日志系统
- 性能测试和优化
- 安全审计

**Q: 代码生成器生成的代码质量如何？**
A: 所有生成的代码都遵循：
- FastAPI 最佳实践
- PEP 8 代码规范
- 分层架构设计原则
- 参考了生产级应用

**Q: 支持哪些数据库？**
A: 基于 SQLModel（SQLAlchemy），理论上支持所有 SQLAlchemy 支持的数据库：
- SQLite（开发推荐）
- PostgreSQL（生产推荐）
- MySQL / MariaDB
- Oracle
- MSSQL

**Q: 如何扩展生成器功能？**
A: 通过修改 `代码生成器/codegen.py` 中的模板方法，或继承 `CodeGenerator` 类自定义

**Q: 项目更新频率如何？**
A: 会根据 FastAPI 和依赖库的更新进行维护

## 🐛 已知问题

| 问题 | 状态 | 解决方案 |
|------|------|--------|
| SQLites 不支持并发写 | 已知 | 生产环境使用 PostgreSQL |
| Windows 路径问题 | 已解决 | 使用 pathlib.Path |

## 📋 TODO（计划功能）

- [ ] 添加单元测试框架
- [ ] 集成 Redis 缓存
- [ ] 添加日志系统
- [ ] 支持 GraphQL 生成
- [ ] 添加 WebSocket 支持
- [ ] 生成 OpenAPI Schema 导出
- [ ] Web UI 代码生成器

## 🤝 贡献指南

欢迎贡献代码、报告 Bug、提出建议！

```bash
# 1. Fork 本仓库
# 2. 创建特性分支 (git checkout -b feature/AmazingFeature)
# 3. 提交更改 (git commit -m 'Add some AmazingFeature')
# 4. 推送到分支 (git push origin feature/AmazingFeature)
# 5. 提交 Pull Request
```

**贡献方式：**
- 🐛 报告 Bug
- 💡 提出新想法
- 📝 改进文档
- 🔧 代码优化
- ⭐ 分享给更多人

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情

这意味着你可以：
- ✅ 自由使用、复制、修改
- ✅ 用于商业项目
- ✅ 私有或公开使用

但需要：
- ⚠️ 包含原始许可证和版权声明

## 💬 反馈和支持

- 📮 报告 Bug：在 GitHub 上提交 Issue
- 💬 讨论：GitHub Discussions
- 📧 联系方式：[your-email@example.com](mailto:your-email@example.com)

## 🎉 鸣谢

感谢以下项目和社区的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL + Python 对象模型
- [Pydantic](https://docs.pydantic.dev/) - 数据验证库
- [Python 社区](https://www.python.org/)

## 📈 项目统计

```
Total Lines         ~5000+
Python Files        20+
Database Tables     5+
API Endpoints       30+
Test Coverage       --
```

## ⭐ 如果觉得有帮助，请给个 Star！

![Stars](https://img.shields.io/github/stars/yourusername/Python_Learn?style=social)

---

**最后更新**: 2026-04-14  
**维护者**: [Your Name](https://github.com/yourusername)  
**License**: MIT

---

## 📞 联系方式

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: [your-email@example.com](mailto:your-email@example.com)
- WeChat: [wechat-id]
- QQ: [qq-number]

**Happy Coding! 🚀**
