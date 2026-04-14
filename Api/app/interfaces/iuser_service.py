"""
app/interfaces/iuser_service.py — 用户 Service 接口

继承 IBaseService，在标准 CRUD 基础上扩展用户特有的业务方法。
"""
from abc import abstractmethod
from typing import Optional, List

from app.interfaces.ibase_service import IBaseService
from app.entity.user_entity import (
    User, UserCreate, UserUpdate, UserResponse,
    UserPageQuery, LoginRequest, LoginResponse, ChangePasswordRequest,
)
from app.core.response import PageResult


class IUserService(IBaseService[User, UserCreate, UserUpdate, UserResponse]):
    """
    用户 Service 接口
    """

    @abstractmethod
    async def login(self, dto: LoginRequest) -> LoginResponse:
        """用户名 + 密码登录，返回 JWT token"""
        ...

    @abstractmethod
    async def get_by_username(self, user_name: str) -> Optional[UserResponse]:
        """根据用户名精确查询"""
        ...

    @abstractmethod
    async def page_query(self, query: UserPageQuery) -> PageResult[UserResponse]:
        """分页查询（支持用户名模糊搜索）"""
        ...

    @abstractmethod
    async def change_password(self, user_id: int, dto: ChangePasswordRequest) -> bool:
        """修改密码：校验原密码后更新为新密码"""
        ...

    @abstractmethod
    async def batch_delete(self, ids: List[int]) -> int:
        """批量删除，返回成功删除数量"""
        ...