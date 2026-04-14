"""
app/services/user_service.py — 用户 Service 实现

实现 IUserService 定义的全部业务契约。
"""
import math
from typing import Optional, List

from sqlmodel import Session, select, func

from app.services.base_service import BaseService
from app.interfaces.iuser_service import IUserService
from app.entity.user_entity import (
    User, UserCreate, UserUpdate, UserResponse,
    UserPageQuery, LoginRequest, LoginResponse, ChangePasswordRequest,
)
from app.core.response import PageResult
from app.core.exceptions import AppException, NotFoundException
from app.core.security import hash_password, verify_password, create_access_token


class UserService(
    BaseService[User, UserCreate, UserUpdate, UserResponse],
    IUserService,
):
    """用户业务逻辑实现"""

    def __init__(self, session: Session):
        super().__init__(
            session=session,
            entity_class=User,
            response_class=UserResponse,
            pk_field="user_id",
        )

    # ------------------------------------------------------------------ #
    #  登录
    # ------------------------------------------------------------------ #

    async def login(self, dto: LoginRequest) -> LoginResponse:
        """校验用户名 + 密码，通过后签发 JWT"""
        # 查原始实体（含 password 字段）
        stmt = select(User).where(User.user_name == dto.user_name)
        user = self.session.exec(stmt).first()

        if not user:
            raise AppException("用户名或密码错误", code=401)
        if not verify_password(dto.password, user.password):
            raise AppException("用户名或密码错误", code=401)

        token = create_access_token(user_id=user.user_id, user_name=user.user_name)
        return LoginResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    # ------------------------------------------------------------------ #
    #  create
    # ------------------------------------------------------------------ #

    async def create(self, dto: UserCreate) -> UserResponse:
        # 用户名唯一性校验
        existing = await self.get_by_username(dto.user_name)
        if existing:
            raise AppException(f"用户名 '{dto.user_name}' 已存在")

        user = User(
            user_name=dto.user_name,
            password=hash_password(dto.password),   # bcrypt 加密存储
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserResponse.model_validate(user)

    # ------------------------------------------------------------------ #
    #  update
    # ------------------------------------------------------------------ #

    async def update(self, user_id: int, dto: UserUpdate) -> UserResponse:
        user = self._get_entity(user_id)

        if dto.user_name and dto.user_name != user.user_name:
            conflict = await self.get_by_username(dto.user_name)
            if conflict:
                raise AppException(f"用户名 '{dto.user_name}' 已被占用")
            user.user_name = dto.user_name

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserResponse.model_validate(user)

    # ------------------------------------------------------------------ #
    #  修改密码
    # ------------------------------------------------------------------ #

    async def change_password(self, user_id: int, dto: ChangePasswordRequest) -> bool:
        """校验原密码后，将新密码加密存储"""
        user = self._get_entity(user_id)

        if not verify_password(dto.old_password, user.password):
            raise AppException("原密码错误")

        user.password = hash_password(dto.new_password)
        self.session.add(user)
        self.session.commit()
        return True

    # ------------------------------------------------------------------ #
    #  扩展查询
    # ------------------------------------------------------------------ #

    async def get_by_username(self, user_name: str) -> Optional[UserResponse]:
        """根据用户名精确查询（返回 DTO，不含密码）"""
        stmt = select(User).where(User.user_name == user_name)
        user = self.session.exec(stmt).first()
        return UserResponse.model_validate(user) if user else None

    async def page_query(self, query: UserPageQuery) -> PageResult[UserResponse]:
        """分页查询，支持用户名模糊搜索"""
        stmt = select(User)
        if query.keyword:
            stmt = stmt.where(User.user_name.contains(query.keyword))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.exec(count_stmt).one()

        offset = (query.page - 1) * query.page_size
        users = self.session.exec(stmt.offset(offset).limit(query.page_size)).all()

        return PageResult(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=math.ceil(total / query.page_size) if total > 0 else 1,
        )

    # ------------------------------------------------------------------ #
    #  批量操作
    # ------------------------------------------------------------------ #

    async def batch_delete(self, ids: List[int]) -> int:
        """批量删除，返回实际删除数量"""
        stmt = select(User).where(User.user_id.in_(ids))
        users = self.session.exec(stmt).all()
        for user in users:
            self.session.delete(user)
        self.session.commit()
        return len(users)