"""
app/interfaces/ibase_service.py — 通用 CRUD Service 抽象接口

定义所有 Service 的标准契约，面向接口编程，解耦实现层。
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

EntityT = TypeVar("EntityT")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")
ResponseT = TypeVar("ResponseT")


class IBaseService(ABC, Generic[EntityT, CreateT, UpdateT, ResponseT]):
    """
    基础 Service 接口（抽象）
    定义标准 CRUD 的方法签名
    """

    @abstractmethod
    async def create(self, dto: CreateT) -> ResponseT:
        """新增"""
        ...

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[ResponseT]:
        """根据 ID 查询，不存在则抛出 NotFoundException"""
        ...

    @abstractmethod
    async def update(self, entity_id: int, dto: UpdateT) -> ResponseT:
        """根据 ID 更新，不存在则抛出 NotFoundException"""
        ...

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """根据 ID 删除，返回是否成功"""
        ...

    @abstractmethod
    async def list_all(self) -> List[ResponseT]:
        """查询全部记录"""
        ...