"""
代码生成器使用指南 (Code Generator User Guide)

本生成器可以根据实体定义自动生成完整的 Entity、Service、Controller 代码。
"""

# ========================================================================
# 快速开始 (Quick Start)
# ========================================================================

# 方法 1：使用内置示例
python codegen.py generate --entity post
python codegen.py generate --entity comment

# 方法 2：指定中文名称（可选）
python codegen.py generate --entity post --display-name "博客文章"

# 方法 3：指定输出目录（默认: Api）
python codegen.py generate --entity post --output ./Api


# ========================================================================
# 详细使用步骤
# ========================================================================

## 1. 定义实体配置 (entities_config.py)

在 entities_config.py 中定义你的实体：

    PRODUCT_CONFIG = EntityConfig(
        name="product",                    # 表名（英文，单数）
        display_name="商品",               # 中文显示名
        fields=[
            FieldConfig(
                name="name",
                type_hint="str",
                description="商品名称",
                max_length=100,
                unique=True,
                index=True,
            ),
            FieldConfig(
                name="price",
                type_hint="float",
                description="商品价格",
            ),
            FieldConfig(
                name="category",
                type_hint="str",
                description="商品分类",
                max_length=50,
            ),
        ],
        has_auth=True,  # 是否需要认证
    )

    ENTITIES = {
        "product": PRODUCT_CONFIG,
    }


## 2. 运行生成器

    python codegen.py generate --entity product


## 3. 查看生成的文件

生成的文件将保存到以下位置：

    Api/
    ├── app/
    │   ├── entity/
    │   │   └── product_entity.py          # Entity & DTO
    │   ├── interfaces/
    │   │   └── iproduct_service.py        # Service Interface
    │   ├── services/
    │   │   └── product_service.py         # Service Implementation
    │   └── controllers/
    │       └── product_controller.py      # API Routes


## 4. 集成到 main.py

在 main.py 中注册路由：

    from app.controllers import product_controller
    
    app.include_router(
        product_controller.router,
        prefix="/api/v1",
        tags=["商品管理"]
    )


# ========================================================================
# FieldConfig 字段配置说明
# ========================================================================

FieldConfig 参数详解：

    name: str                    # 字段名（英文，蛇形命名）
    type_hint: str              # 类型提示（"str", "int", "float" 等）
    db_type: str                # 数据库类型（默认 "str"）
    required: bool              # 是否必填（默认 True）
    unique: bool                # 是否唯一（默认 False）
    index: bool                 # 是否建立索引（默认 False）
    description: str            # 字段描述（用于 Swagger 文档）
    max_length: Optional[int]   # 最大长度（仅字符串适用）


# ========================================================================
# 生成代码的主要特性
# ========================================================================

生成的代码包含以下特性：

✓ 完整的 Entity 定义（database entity）
✓ 强类型 DTO（Create, Update, Response）
✓ Service 业务逻辑层（CRUD + 分页）
✓ Service Interface（便于扩展和测试）
✓ RESTful Controller（FastAPI router）
✓ 完整的 Swagger 文档注解
✓ 认证支持（可选）
✓ 分页查询支持
✓ 批量删除支持
✓ 参考项目代码的最佳实践


# ========================================================================
# 自定义生成后的代码
# ========================================================================

生成的代码是基础模板，你可以：

1. 在 Service 中添加自定义业务逻辑
   - 例如：add_discount()、validate_stock() 等
   - Service 中已有占位符注释

2. 在 Controller 中添加自定义路由
   - 例如：搜索、过滤、导出等功能

3. 在 Entity 中添加关联关系
   - 添加 ForeignKey、relationship 等

4. 在 DTO 中添加验证规则
   - 使用 pydantic validators


# ========================================================================
# 常见场景示例
# ========================================================================

## 场景 1：商品管理系统

    PRODUCT_CONFIG = EntityConfig(
        name="product",
        display_name="商品",
        fields=[
            FieldConfig(name="name", type_hint="str", description="商品名", max_length=100, unique=True),
            FieldConfig(name="price", type_hint="float", description="价格"),
            FieldConfig(name="stock", type_hint="int", description="库存"),
            FieldConfig(name="category", type_hint="str", description="分类", max_length=50),
            FieldConfig(name="description", type_hint="str", description="描述", max_length=500),
        ],
        has_auth=True,
    )


## 场景 2：文章评论系统

    POST_CONFIG = EntityConfig(
        name="post",
        display_name="文章",
        fields=[
            FieldConfig(name="title", type_hint="str", description="标题", max_length=200, unique=True),
            FieldConfig(name="content", type_hint="str", description="内容"),
            FieldConfig(name="author", type_hint="str", description="作者", max_length=50),
        ],
        has_auth=True,
    )

    COMMENT_CONFIG = EntityConfig(
        name="comment",
        display_name="评论",
        fields=[
            FieldConfig(name="content", type_hint="str", description="内容"),
            FieldConfig(name="post_id", type_hint="int", description="文章ID"),
            FieldConfig(name="author", type_hint="str", description="评论者", max_length=50),
        ],
        has_auth=True,
    )


# ========================================================================
# 故障排查 (Troubleshooting)
# ========================================================================

Q: 生成的文件存储位置不对？
A: 检查 --output 参数，默认输出到 Api 目录

Q: 代码格式不符合我的要求？
A: 修改 codegen.py 中的 generate_* 方法来自定义模板

Q: 需要添加新的生成模板（如 Model, Validator）？
A: 在 CodeGenerator 类中添加新的 generate_* 方法

Q: 如何生成关联关系（外键）？
A: 手动编辑生成的 entity 文件，添加 relationship 定义


# ========================================================================
# 高级用法
# ========================================================================

## 扩展生成器

继承 CodeGenerator 类添加自定义功能：

    from codegen import CodeGenerator, EntityConfig
    
    class MyCodeGenerator(CodeGenerator):
        def generate_model(self, config: EntityConfig) -> str:
            # 生成自定义 Model 类
            pass
        
        def generate_validator(self, config: EntityConfig) -> str:
            # 生成自定义 Validator 类
            pass


## 批量生成

    from entities_config import ENTITIES
    from codegen import CodeGenerator
    
    generator = CodeGenerator()
    for entity_name, entity_config in ENTITIES.items():
        generator.save_files(entity_config)
        print(f"✓ 生成 {entity_name}")


"""

print(__doc__)
