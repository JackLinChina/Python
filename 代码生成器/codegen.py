"""
代码生成器 - 根据实体定义自动生成 Entity、Service、Controller

使用方法：
    python codegen.py generate --entity post

配置方式：创建 entities_config.py 定义实体
"""
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FieldConfig:
    """字段配置"""
    name: str
    type_hint: str
    db_type: str = "str"
    required: bool = True
    unique: bool = False
    index: bool = False
    description: str = ""
    max_length: Optional[int] = None


@dataclass
class EntityConfig:
    """实体配置"""
    name: str  # 表名（如 'post', 'comment'）
    display_name: str  # 中文显示名（如 '文章'）
    fields: List[FieldConfig]  # 字段列表
    has_auth: bool = True  # 是否需要认证


class CodeGenerator:
    """代码生成器"""
    
    def __init__(self, base_path: str = "Api"):
        self.base_path = Path(base_path)
        self.app_path = self.base_path / "app"
    
    def generate_entity(self, config: EntityConfig) -> str:
        """生成 Entity 代码"""
        name = config.name
        display_name = config.display_name
        
        # PK 字段名（如 post_id, comment_id）
        pk_field = f"{name}_id"
        
        # 生成字段定义
        fields_code = self._generate_entity_fields(config, pk_field)
        dto_fields_code = self._generate_dto_fields(config)
        
        entity_code = f'''"""
app/entity/{name}_entity.py — {display_name}实体 & DTO

数据库表：{name}s
"""
from typing import Optional
from sqlmodel import SQLModel, Field


# ======== 数据库实体 ========

class {self._to_class_name(name)}(SQLModel, table=True):
    """{display_name}表实体，对应数据库 {name}s 表"""
    __tablename__ = "{name}s"

{fields_code}


# ======== 请求 DTO ========

class {self._to_class_name(name)}Create(SQLModel):
    """{display_name}创建 — 请求体"""
{dto_fields_code}


class {self._to_class_name(name)}Update(SQLModel):
    """{display_name}更新 — 请求体（字段均可选）"""
{self._generate_update_dto_fields(config)}


# ======== 响应 DTO ========

class {self._to_class_name(name)}Response(SQLModel):
    """{display_name}响应 — DTO"""
{self._generate_response_dto_fields(config, pk_field)}
    
    class Config:
        from_attributes = True
'''
        return entity_code
    
    def generate_interface(self, config: EntityConfig) -> str:
        """生成 Service Interface"""
        name = config.name
        class_name = self._to_class_name(name)
        display_name = config.display_name
        
        interface_code = f'''"""
app/interfaces/i{name}_service.py — {display_name}Service 接口
"""
from typing import Optional, List
from abc import ABC, abstractmethod
from app.entity.{name}_entity import (
    {class_name}, {class_name}Create, {class_name}Update, {class_name}Response
)
from app.core.response import PageResult


class I{class_name}Service(ABC):
    """{display_name}业务服务接口"""
    
    @abstractmethod
    async def get_by_id(self, {name}_id: int) -> {class_name}Response:
        """根据 ID 查询"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[{class_name}Response]:
        """查询所有"""
        pass
    
    @abstractmethod
    async def create(self, dto: {class_name}Create) -> {class_name}Response:
        """创建"""
        pass
    
    @abstractmethod
    async def update(self, {name}_id: int, dto: {class_name}Update) -> {class_name}Response:
        """更新"""
        pass
    
    @abstractmethod
    async def delete(self, {name}_id: int) -> bool:
        """删除"""
        pass
    
    @abstractmethod
    async def get_page(self, page: int, page_size: int) -> PageResult[{class_name}Response]:
        """分页查询"""
        pass
'''
        return interface_code
    
    def generate_service(self, config: EntityConfig) -> str:
        """生成 Service 实现"""
        name = config.name
        class_name = self._to_class_name(name)
        display_name = config.display_name
        pk_field = f"{name}_id"
        
        service_code = f'''"""
app/services/{name}_service.py — {display_name}Service 实现

实现 I{class_name}Service 定义的全部业务契约。
"""
from typing import Optional, List
import math
from sqlmodel import Session, select, func

from app.services.base_service import BaseService
from app.interfaces.i{name}_service import I{class_name}Service
from app.entity.{name}_entity import (
    {class_name}, {class_name}Create, {class_name}Update, {class_name}Response
)
from app.core.response import PageResult
from app.core.exceptions import AppException, NotFoundException


class {class_name}Service(
    BaseService[{class_name}, {class_name}Create, {class_name}Update, {class_name}Response],
    I{class_name}Service,
):
    """{display_name}业务逻辑实现"""
    
    def __init__(self, session: Session):
        super().__init__(
            session=session,
            entity_class={class_name},
            response_class={class_name}Response,
            pk_field="{pk_field}",
        )
    
    # ================================================================== #
    #  自定义业务方法（按需扩展）
    # ================================================================== #
    
    # 示例：添加按名称查询
    # async def get_by_name(self, name: str) -> Optional[{class_name}Response]:
    #     """按名称查询"""
    #     stmt = select({class_name}).where({class_name}.name == name)
    #     entity = self.session.exec(stmt).first()
    #     return {class_name}Response.model_validate(entity) if entity else None
'''
        return service_code
    
    def generate_controller(self, config: EntityConfig) -> str:
        """生成 Controller"""
        name = config.name
        class_name = self._to_class_name(name)
        display_name = config.display_name
        pk_field = f"{name}_id"
        
        auth_dep = ", _: TokenPayload = Depends(get_current_user)" if config.has_auth else ""
        
        controller_code = f'''"""
app/controllers/{name}_controller.py — {display_name}Controller（路由层）

接口清单：
  需要 Token（Authorization: Bearer <token>）：
    POST   /api/v1/{name}s                   创建{display_name}
    GET    /api/v1/{name}s                   查询所有{display_name}
    GET    /api/v1/{name}s/page/list         分页查询
    GET    /api/v1/{name}s/{{{pk_field}}}    根据 ID 查询
    PUT    /api/v1/{name}s/{{{pk_field}}}    修改{display_name}
    DELETE /api/v1/{name}s/{{{pk_field}}}    删除{display_name}
    DELETE /api/v1/{name}s/batch/delete      批量删除
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.core.response import ResponseModel, PageResult
from app.core.security import get_current_user, TokenPayload
from app.entity.{name}_entity import (
    {class_name}Create, {class_name}Update, {class_name}Response
)
from app.services.{name}_service import {class_name}Service

router = APIRouter()


# ================================================================== #
#  依赖注入
# ================================================================== #

def get_{name}_service(session: Session = Depends(get_session)) -> {class_name}Service:
    return {class_name}Service(session)


# ================================================================== #
#  基础 CRUD
# ================================================================== #

@router.post(
    "/{name}s",
    response_model=ResponseModel[{class_name}Response],
    tags=["{display_name}管理"],
    summary="创建{display_name}",
)
async def create_{name}(
    dto: {class_name}Create,
    service: {class_name}Service = Depends(get_{name}_service),{auth_dep}
):
    data = await service.create(dto)
    return ResponseModel.ok(data=data, message="{display_name}创建成功")


@router.get(
    "/{name}s/{{{pk_field}}}",
    response_model=ResponseModel[{class_name}Response],
    tags=["{display_name}管理"],
    summary="根据 ID 查询{display_name}",
)
async def get_{name}(
    {pk_field}: int,
    service: {class_name}Service = Depends(get_{name}_service),{auth_dep}
):
    data = await service.get_by_id({pk_field})
    return ResponseModel.ok(data=data)


@router.get(
    "/{name}s",
    response_model=ResponseModel[List[{class_name}Response]],
    tags=["{display_name}管理"],
    summary="查询所有{display_name}",
)
async def get_all_{name}s(
    service: {class_name}Service = Depends(get_{name}_service),{auth_dep}
):
    data = await service.get_all()
    return ResponseModel.ok(data=data)


@router.put(
    "/{name}s/{{{pk_field}}}",
    response_model=ResponseModel[{class_name}Response],
    tags=["{display_name}管理"],
    summary="修改{display_name}",
)
async def update_{name}(
    {pk_field}: int,
    dto: {class_name}Update,
    service: {class_name}Service = Depends(get_{name}_service),{auth_dep}
):
    data = await service.update({pk_field}, dto)
    return ResponseModel.ok(data=data, message="修改成功")


@router.delete(
    "/{name}s/{{{pk_field}}}",
    response_model=ResponseModel[bool],
    tags=["{display_name}管理"],
    summary="删除{display_name}",
)
async def delete_{name}(
    {pk_field}: int,
    service: {class_name}Service = Depends(get_{name}_service),{auth_dep}
):
    result = await service.delete({pk_field})
    return ResponseModel.ok(data=result, message="删除成功")


@router.get(
    "/{name}s/page/list",
    response_model=ResponseModel[PageResult[{class_name}Response]],
    tags=["{display_name}管理"],
    summary="分页查询{display_name}",
)
async def get_{name}s_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: {class_name}Service = Depends(get_{name}_service),{auth_dep}
):
    data = await service.get_page(page, page_size)
    return ResponseModel.ok(data=data)


@router.delete(
    "/{name}s/batch/delete",
    response_model=ResponseModel[bool],
    tags=["{display_name}管理"],
    summary="批量删除{display_name}",
)
async def batch_delete_{name}s(
    ids: List[int] = Query(...),
    service: {class_name}Service = Depends(get_{name}_service),{auth_dep}
):
    result = await service.delete_batch(ids)
    return ResponseModel.ok(data=result, message="批量删除成功")
'''
        return controller_code
    
    def _generate_entity_fields(self, config: EntityConfig, pk_field: str) -> str:
        """生成实体字段代码"""
        lines = [f'    {pk_field}: Optional[int] = Field(']
        lines.append('        default=None,')
        lines.append('        primary_key=True,')
        lines.append(f'        description="{config.display_name}主键 ID（自增）",')
        lines.append('    )')
        
        for field in config.fields:
            lines.append(f'    {field.name}: str = Field(')
            if field.max_length:
                lines.append(f'        max_length={field.max_length},')
            if field.unique:
                lines.append('        unique=True,')
            if field.index:
                lines.append('        index=True,')
            lines.append(f'        description="{field.description}",')
            lines.append('    )')
        
        return '\n'.join(lines)
    
    def _generate_dto_fields(self, config: EntityConfig) -> str:
        """生成创建 DTO 字段"""
        lines = []
        for field in config.fields:
            constraint = ""
            if field.max_length:
                constraint += f", max_length={field.max_length}"
            lines.append(f'    {field.name}: str = Field(description="{field.description}"{constraint})')
        return '\n'.join(lines) if lines else '    pass'
    
    def _generate_update_dto_fields(self, config: EntityConfig) -> str:
        """生成更新 DTO 字段"""
        lines = []
        for field in config.fields:
            constraint = ""
            if field.max_length:
                constraint += f", max_length={field.max_length}"
            lines.append(f'    {field.name}: Optional[str] = Field(default=None, description="{field.description}"{constraint})')
        return '\n'.join(lines) if lines else '    pass'
    
    def _generate_response_dto_fields(self, config: EntityConfig, pk_field: str) -> str:
        """生成响应 DTO 字段"""
        lines = [f'    {pk_field}: int']
        for field in config.fields:
            lines.append(f'    {field.name}: str')
        return '\n'.join(lines)
    
    def _to_class_name(self, name: str) -> str:
        """将表名转换为类名（驼峰命名）"""
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts)
    
    def save_files(self, config: EntityConfig, output_dir: str = "Api"):
        """保存生成的文件"""
        base_path = Path(output_dir)
        name = config.name
        
        # 保存 Entity
        entity_path = base_path / "app" / "entity" / f"{name}_entity.py"
        entity_path.parent.mkdir(parents=True, exist_ok=True)
        entity_path.write_text(self.generate_entity(config), encoding='utf-8')
        print(f"✓ 生成 Entity: {entity_path}")
        
        # 保存 Interface
        interface_path = base_path / "app" / "interfaces" / f"i{name}_service.py"
        interface_path.parent.mkdir(parents=True, exist_ok=True)
        interface_path.write_text(self.generate_interface(config), encoding='utf-8')
        print(f"✓ 生成 Interface: {interface_path}")
        
        # 保存 Service
        service_path = base_path / "app" / "services" / f"{name}_service.py"
        service_path.parent.mkdir(parents=True, exist_ok=True)
        service_path.write_text(self.generate_service(config), encoding='utf-8')
        print(f"✓ 生成 Service: {service_path}")
        
        # 保存 Controller
        controller_path = base_path / "app" / "controllers" / f"{name}_controller.py"
        controller_path.parent.mkdir(parents=True, exist_ok=True)
        controller_path.write_text(self.generate_controller(config), encoding='utf-8')
        print(f"✓ 生成 Controller: {controller_path}")


def main():
    parser = argparse.ArgumentParser(description="代码生成器")
    parser.add_argument("command", choices=["generate"], help="命令")
    parser.add_argument("--entity", required=True, help="实体名称（如 post, comment）")
    parser.add_argument("--display-name", help="中文显示名（如 文章）")
    parser.add_argument("--output", default="Api", help="输出目录")
    
    args = parser.parse_args()
    
    # 默认配置示例
    if args.entity == "post":
        config = EntityConfig(
            name="post",
            display_name=args.display_name or "文章",
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
    elif args.entity == "comment":
        config = EntityConfig(
            name="comment",
            display_name=args.display_name or "评论",
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
            ],
            has_auth=True,
        )
    else:
        print(f"❌ 未知实体: {args.entity}")
        print("✓ 支持的实体: post, comment")
        return
    
    generator = CodeGenerator()
    generator.save_files(config, args.output)


if __name__ == "__main__":
    main()
