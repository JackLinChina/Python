#!/usr/bin/env python3
"""
快速示例 - 演示如何使用代码生成器

运行此脚本来快速生成示例代码：
    python example_usage.py
"""

from codegen import CodeGenerator, EntityConfig, FieldConfig


def example_1_generate_post():
    """示例 1: 生成文章(Post)模块"""
    print("\n" + "="*60)
    print("示例 1: 生成文章(Post)模块")
    print("="*60)
    
    config = EntityConfig(
        name="post",
        display_name="文章",
        fields=[
            FieldConfig(
                name="title",
                type_hint="str",
                description="文章标题",
                max_length=200,
                unique=True,
                index=True,
            ),
            FieldConfig(
                name="content",
                type_hint="str",
                description="文章内容",
            ),
            FieldConfig(
                name="author",
                type_hint="str",
                description="作者",
                max_length=50,
            ),
        ],
        has_auth=True,
    )
    
    generator = CodeGenerator()
    generator.save_files(config, "Api")


def example_2_generate_product():
    """示例 2: 生成商品(Product)模块"""
    print("\n" + "="*60)
    print("示例 2: 生成商品(Product)模块")
    print("="*60)
    
    config = EntityConfig(
        name="product",
        display_name="商品",
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
                type_hint="str",
                description="商品价格",
                max_length=20,
            ),
            FieldConfig(
                name="category",
                type_hint="str",
                description="商品分类",
                max_length=50,
            ),
            FieldConfig(
                name="stock",
                type_hint="str",
                description="库存数量",
                max_length=10,
            ),
            FieldConfig(
                name="description",
                type_hint="str",
                description="商品描述",
                max_length=500,
            ),
        ],
        has_auth=True,
    )
    
    generator = CodeGenerator()
    generator.save_files(config, "Api")


def example_3_generate_task():
    """示例 3: 生成任务(Task)模块"""
    print("\n" + "="*60)
    print("示例 3: 生成任务(Task)模块")
    print("="*60)
    
    config = EntityConfig(
        name="task",
        display_name="任务",
        fields=[
            FieldConfig(
                name="title",
                type_hint="str",
                description="任务标题",
                max_length=200,
            ),
            FieldConfig(
                name="description",
                type_hint="str",
                description="任务描述",
                max_length=500,
            ),
            FieldConfig(
                name="status",
                type_hint="str",
                description="任务状态(pending/processing/completed)",
                max_length=50,
            ),
            FieldConfig(
                name="priority",
                type_hint="str",
                description="优先级(low/medium/high)",
                max_length=20,
            ),
        ],
        has_auth=True,
    )
    
    generator = CodeGenerator()
    generator.save_files(config, "Api")


def show_generated_code():
    """展示生成的代码示例"""
    print("\n" + "="*60)
    print("代码示例: Entity 代码片段")
    print("="*60)
    
    config = EntityConfig(
        name="article",
        display_name="文章",
        fields=[
            FieldConfig(
                name="title",
                type_hint="str",
                description="标题",
                max_length=200,
            ),
            FieldConfig(
                name="content",
                type_hint="str",
                description="内容",
            ),
        ],
        has_auth=True,
    )
    
    generator = CodeGenerator()
    entity_code = generator.generate_entity(config)
    print(entity_code[:500] + "\n... (已截断)")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("代码生成器 - 快速示例")
    print("="*60)
    print("\n本脚本演示如何使用代码生成器生成 Entity、Service、Controller 代码")
    print("\n选择要运行的示例:")
    print("  1. 生成文章(Post)模块")
    print("  2. 生成商品(Product)模块")
    print("  3. 生成任务(Task)模块")
    print("  4. 查看代码示例")
    print("  5. 全部生成")
    print("  0. 退出")
    
    choice = input("\n请选择 (0-5): ").strip()
    
    if choice == "1":
        example_1_generate_post()
    elif choice == "2":
        example_2_generate_product()
    elif choice == "3":
        example_3_generate_task()
    elif choice == "4":
        show_generated_code()
    elif choice == "5":
        example_1_generate_post()
        example_2_generate_product()
        example_3_generate_task()
        print("\n✓ 全部生成完成！")
    else:
        print("已退出")
    
    print("\n" + "="*60)
    print("下一步：")
    print("  1. 编辑生成的文件，添加自定义业务逻辑")
    print("  2. 在 main.py 中注册路由")
    print("  3. 运行应用: python main.py")
    print("="*60)


if __name__ == "__main__":
    main()
