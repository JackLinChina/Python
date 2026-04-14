# 代码生成器系统完整指南

## 📋 项目结构

```
Api/
├── codegen.py                  # ⭐ 核心生成器（基础功能）
├── codegen_advanced.py         # 高级生成器（支持配置文件）
├── entities_config.py          # 实体配置文件（定义要生成的实体）
├── example_usage.py            # 快速示例脚本
├── CODEGEN_GUIDE.md           # 详细使用指南
├── README.md                   # 本文件
│
├── app/
│   ├── controllers/            # API 路由层
│   │   ├── user_controller.py  # (已有)
│   │   ├── post_controller.py  # (生成的)
│   │   └── ...
│   │
│   ├── services/               # 业务逻辑层
│   │   ├── user_service.py     # (已有)
│   │   ├── post_service.py     # (生成的)
│   │   └── ...
│   │
│   ├── entity/                 # 数据模型层
│   │   ├── user_entity.py      # (已有)
│   │   ├── post_entity.py      # (生成的)
│   │   └── ...
│   │
│   ├── interfaces/             # 服务接口定义
│   │   ├── iuser_service.py    # (已有)
│   │   ├── ipost_service.py    # (生成的)
│   │   └── ...
│   │
│   └── core/
│       ├── config.py
│       ├── database.py
│       ├── exceptions.py
│       ├── response.py
│       └── security.py
│
└── main.py
```

---

## 🚀 快速开始（3步搞定）

### 步骤 1️⃣: 定义实体配置

编辑 `entities_config.py`，定义你的实体（以商品为例）：

```python
PRODUCT_CONFIG = EntityConfig(
    name="product",                  # 表名
    display_name="商品",             # 中文名
    fields=[
        FieldConfig(
            name="name",
            type_hint="str",
            description="商品名称",
            max_length=100,
            unique=True,
        ),
        FieldConfig(
            name="price",
            type_hint="str",
            description="商品价格",
        ),
        FieldConfig(
            name="category",
            type_hint="str",
            description="商品分类",
            max_length=50,
        ),
    ],
    has_auth=True,  # 需要认证
)

ENTITIES = {
    "product": PRODUCT_CONFIG,
}
```

### 步骤 2️⃣: 运行生成器

```bash
# 基础生成器（需要预定义配置）
python codegen.py generate --entity product

# 或使用高级生成器（自动读取配置文件）
python codegen_advanced.py --entity product

# 或使用可视化界面
python example_usage.py
```

### 步骤 3️⃣: 注册路由到 main.py

```python
# app/main.py
from fastapi import FastAPI
from app.controllers import product_controller

app = FastAPI()

# 注册商品模块路由
app.include_router(
    product_controller.router,
    prefix="/api/v1",
    tags=["商品管理"]
)
```

✅ 完成！现在你有了完整的商品管理 API！

---

## 📝 生成器类型及对比

| 特性 | codegen.py | codegen_advanced.py | example_usage.py |
|------|-----------|-------------------|-----------------|
| 学习难度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐ 简单 |
| 功能完整性 | 基础 | 完整 | 演示 |
| 配置方式 | 命令行参数 | 配置文件 | 交互式菜单 |
| 推荐用途 | 学习 | **生产环境** | 快速尝试 |
| 支持批量生成 | ❌ | ✅ | ❌ |
| 支持列表实体 | ❌ | ✅ | ❌ |

---

## 💡 常见使用场景

### 场景 1: 快速原型开发

```bash
# 运行交互式示例
python example_usage.py
```

### 场景 2: 生成单个模块

```bash
# 使用基础生成器
python codegen.py generate --entity product
```

### 场景 3: 生成多个模块

```bash
# 编辑 entities_config.py 定义多个实体，然后：
python codegen_advanced.py --all
```

### 场景 4: 生成特定的几个模块

```bash
python codegen_advanced.py --batch post product comment
```

### 场景 5: 查看可用的实体

```bash
python codegen_advanced.py --list
```

---

## 🎯 生成代码的内容

每个实体生成 **4 个文件**：

### 1. Entity 文件 (app/entity/{name}_entity.py)
- 数据库实体（SQLModel）
- Create DTO（创建请求体）
- Update DTO（更新请求体）
- Response DTO（响应体）

### 2. Service Interface (app/interfaces/i{name}_service.py)
- 定义服务契约
- 抽象方法定义

### 3. Service 实现 (app/services/{name}_service.py)
- CRUD 操作实现
- 分页查询实现
- 扩展业务逻辑的占位符

### 4. Controller (app/controllers/{name}_controller.py)
- RESTful API 路由
- 请求/响应处理
- Swagger 文档注解
- 认证验证

**总计**: 每个实体 ~300-400 行生成代码 ✨

---

## 🔧 自定义生成器

### 方法 1: 修改模板

编辑 `codegen.py` 中的 `generate_*` 方法来自定义输出：

```python
def generate_entity(self, config: EntityConfig) -> str:
    # 修改此处改变生成的 Entity 代码
    ...
```

### 方法 2: 继承扩展

```python
from codegen import CodeGenerator

class MyCodeGenerator(CodeGenerator):
    def generate_validator(self, config: EntityConfig) -> str:
        # 添加新的生成方法
        return "..."
```

### 方法 3: 添加新字段类型

在 `FieldConfig` 中扩展支持的字段类型：

```python
@dataclass
class FieldConfig:
    # 添加新属性
    is_enum: bool = False
    enum_values: List[str] = None
```

---

## 📚 API 文档示例

生成的代码自动包含 Swagger 文档：

```
GET  /api/v1/products           # 查询所有商品
POST /api/v1/products           # 创建商品
GET  /api/v1/products/{id}      # 查询单个商品
PUT  /api/v1/products/{id}      # 更新商品
DELETE /api/v1/products/{id}    # 删除商品
GET  /api/v1/products/page/list # 分页查询
DELETE /api/v1/products/batch/delete # 批量删除
```

在浏览器打开 `http://localhost:8000/docs` 查看交互式文档 📖

---

## ⚙️ FieldConfig 配置参数详解

```python
FieldConfig(
    name="user_name",           # 字段名（英文，蛇形命名）
    type_hint="str",            # 类型提示
    db_type="varchar",          # 数据库类型（可选）
    required=True,              # 是否必填
    unique=False,               # 是否唯一性约束
    index=False,                # 是否建立索引（加快查询）
    description="用户名",        # 字段描述（用于 API 文档）
    max_length=50,              # 最大长度（字符串）
)
```

---

## 🛠️ 扩展生成的代码

生成的代码是基础框架，可以扩展：

### 1. Service 中添加业务逻辑

```python
class ProductService(BaseService[...]):
    # 添加自定义方法
    async def get_by_category(self, category: str):
        stmt = select(Product).where(Product.category == category)
        return self.session.exec(stmt).all()
    
    async def apply_discount(self, product_id: int, discount: float):
        product = self._get_entity(product_id)
        product.price = float(product.price) * (1 - discount)
        self.session.add(product)
        self.session.commit()
```

### 2. Controller 中添加自定义路由

```python
@router.get("/products/search")
async def search_products(
    keyword: str = Query(...),
    service: ProductService = Depends(get_product_service),
):
    # 自定义搜索逻辑
    pass
```

### 3. Entity 中添加数据库关联

```python
class Product(SQLModel, table=True):
    ...
    category_id: Optional[int] = Field(foreign_key="category.category_id")
    category: Optional["Category"] = Relationship(back_populates="products")
```

---

## ❓ 常见问题

**Q: 生成的代码能用于生产环境吗？**
A: 是的，代码遵循最佳实践。但建议在生产前：
- 添加数据检验逻辑
- 添加业务异常处理
- 添加日志记录
- 性能测试

**Q: 如何修改生成的代码模式？**
A: 编辑 `codegen.py` 中的 `generate_*` 方法，或继承 `CodeGenerator` 类自定义

**Q: 支持哪些数据库类型？**
A: 基于 SQLModel，支持 SQLite、PostgreSQL、MySQL 等

**Q: 如何生成关联关系（外键）？**
A: 生成后手动在 Entity 文件中添加 `ForeignKey` 和 `Relationship`

---

## 📖 相关文档

- [CODEGEN_GUIDE.md](CODEGEN_GUIDE.md) - 详细使用指南
- [codegen.py](codegen.py) - 核心生成器代码
- [entities_config.py](entities_config.py) - 实体配置文件示例

---

## 🎓 学习路线

```
初级使用 (初学)
  ↓
python example_usage.py          # 运行交互式示例
  ↓
中级使用 (实践)
  ↓
python codegen_advanced.py --list  # 查看已定义实体
python codegen_advanced.py --entity product  # 生成模块
  ↓
高级使用 (扩展)
  ↓
修改 entities_config.py           # 定义自己的实体
修改 codegen.py 模板              # 自定义代码生成
继承 CodeGenerator 类              # 扩展功能
```

---

## 🚢 部署检查清单

生成代码后，部署前请检查：

- [ ] 在 `main.py` 中注册路由
- [ ] 数据库迁移（Alembic）
- [ ] 添加数据验证规则
- [ ] 添加异常处理逻辑
- [ ] 添加日志记录
- [ ] 编写单元测试
- [ ] 文档更新
- [ ] 性能测试
- [ ] 安全审计

---

## 💬 支持

有问题？

1. 查看 `CODEGEN_GUIDE.md` 详细指南
2. 运行 `python example_usage.py` 查看示例
3. 查看生成的代码中的注释
4. 参考项目中的 `user_*` 相关文件作为参考

---

**祝你使用愉快！🎉**
