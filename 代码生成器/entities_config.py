"""
entities_config.py - 实体配置文件

在此文件中定义所有需要自动生成代码的实体。
然后运行: python codegen.py generate

示例：
    python codegen.py generate --entity post
"""

from codegen import EntityConfig, FieldConfig


# 示例实体 1：文章（Post）
POST_CONFIG = EntityConfig(
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
            description="作者名称",
            max_length=50,
        ),
        FieldConfig(
            name="tags",
            type_hint="str",
            description="文章标签（逗号分隔）",
            max_length=200,
        ),
    ],
    has_auth=True,
)


# 示例实体 2：评论（Comment）
COMMENT_CONFIG = EntityConfig(
    name="comment",
    display_name="评论",
    fields=[
        FieldConfig(
            name="content",
            type_hint="str",
            description="评论内容",
        ),
        FieldConfig(
            name="post_id",
            type_hint="int",
            description="所属文章 ID",
        ),
        FieldConfig(
            name="author",
            type_hint="str",
            description="评论者名称",
            max_length=50,
        ),
    ],
    has_auth=True,
)


# 示例实体 3：分类（Category）
CATEGORY_CONFIG = EntityConfig(
    name="category",
    display_name="分类",
    fields=[
        FieldConfig(
            name="name",
            type_hint="str",
            description="分类名称",
            max_length=50,
            unique=True,
        ),
        FieldConfig(
            name="description",
            type_hint="str",
            description="分类描述",
            max_length=500,
        ),
    ],
    has_auth=True,
)


# ================================================================== #
#  实体映射字典（便于快速查询）
# ================================================================== #

ENTITIES = {
    "post": POST_CONFIG,
    "comment": COMMENT_CONFIG,
    "category": CATEGORY_CONFIG,
    # 在这里添加更多实体配置
}


if __name__ == "__main__":
    # 如果直接运行此文件，可以列出所有实体
    print("已定义的实体：")
    for entity_name in ENTITIES.keys():
        print(f"  - {entity_name}")
