"""
app/services/base_service.py — 通用 CRUD Service 基类

提供 get_by_id / list_all / delete 的默认实现。
create / update 由子类根据业务字段自行实现。
"""
from typing import Generic, TypeVar, Optional, List, Type
from sqlmodel import Session, select

from app.interfaces.ibase_service import IBaseService
from app.core.exceptions import NotFoundException

EntityT = TypeVar("EntityT")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")
ResponseT = TypeVar("ResponseT")


class BaseService(
    IBaseService[EntityT, CreateT, UpdateT, ResponseT],
    Generic[EntityT, CreateT, UpdateT, ResponseT],
):
    """
    通用 Service 基类

    子类构造时传入：
      - session       : 数据库会话
      - entity_class  : SQLModel 实体类（如 User）
      - response_class: 响应 DTO 类（如 UserResponse）
      - pk_field      : 主键字段名（默认 "id"，可覆盖）
    """

    def __init__(
        self,
        session: Session,
        entity_class: Type[EntityT],
        response_class: Type[ResponseT],
        pk_field: str = "id",
    ):
        self.session = session
        self.entity_class = entity_class
        self.response_class = response_class
        self.pk_field = pk_field

    def _get_entity(self, entity_id: int) -> EntityT:
        """内部方法：根据主键取实体，不存在则抛异常"""
        entity = self.session.get(self.entity_class, entity_id)
        if entity is None:
            raise NotFoundException(
                f"{self.entity_class.__name__} (id={entity_id}) 不存在"
            )
        return entity

    async def get_by_id(self, entity_id: int) -> Optional[ResponseT]:
        entity = self._get_entity(entity_id)
        return self.response_class.model_validate(entity)

    async def list_all(self) -> List[ResponseT]:
        stmt = select(self.entity_class)
        entities = self.session.exec(stmt).all()
        return [self.response_class.model_validate(e) for e in entities]

    async def delete(self, entity_id: int) -> bool:
        entity = self._get_entity(entity_id)
        self.session.delete(entity)
        self.session.commit()
        return True

    async def create(self, dto: CreateT) -> ResponseT:
        raise NotImplementedError("子类必须实现 create 方法")

    async def update(self, entity_id: int, dto: UpdateT) -> ResponseT:
        raise NotImplementedError("子类必须实现 update 方法")