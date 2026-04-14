"""
app/controllers/user_controller.py — 用户 Controller（路由层）

接口清单：
  公开接口（无需 Token）：
    POST   /api/v1/auth/login              登录，返回 JWT
    POST   /api/v1/users                   注册/新增用户

  需要 Token（Authorization: Bearer <token>）：
    GET    /api/v1/users                   查询所有用户
    GET    /api/v1/users/page/list         分页查询
    GET    /api/v1/users/{user_id}         根据 ID 查询
    GET    /api/v1/users/name/{user_name}  根据用户名查询
    PUT    /api/v1/users/{user_id}         修改用户名
    DELETE /api/v1/users/{user_id}         删除用户
    DELETE /api/v1/users/batch/delete      批量删除
    PATCH  /api/v1/users/{user_id}/password  修改密码
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_session
from app.core.response import ResponseModel, PageResult
from app.core.security import get_current_user, TokenPayload
from app.entity.user_entity import (
    UserCreate, UserUpdate, UserResponse,
    UserPageQuery, LoginRequest, LoginResponse, ChangePasswordRequest,
)
from app.services.user_service import UserService

router = APIRouter()


# ------------------------------------------------------------------ #
#  依赖注入
# ------------------------------------------------------------------ #

def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)


# ================================================================== #
#  Auth — 登录（公开，无需 Token）
# ================================================================== #

@router.post(
    "/auth/login",
    response_model=ResponseModel[LoginResponse],
    tags=["认证"],
    summary="用户登录",
    description="传入用户名和密码，校验通过后返回 JWT access token。",
)
async def login(
    dto: LoginRequest,
    service: UserService = Depends(get_user_service),
):
    data = await service.login(dto)
    return ResponseModel.ok(data=data, message="登录成功")


# ================================================================== #
#  基础 CRUD
# ================================================================== #

@router.post(
    "/users",
    response_model=ResponseModel[UserResponse],
    tags=["用户管理"],
    summary="新增用户",
    description="传入 user_name 和 password 创建用户，密码自动 bcrypt 加密存储。",
)
async def create_user(
    dto: UserCreate,
    service: UserService = Depends(get_user_service),
     _: TokenPayload = Depends(get_current_user),   # 需要登录
):
    data = await service.create(dto)
    return ResponseModel.ok(data=data, message="用户创建成功")


@router.get(
    "/users/{user_id}",
    response_model=ResponseModel[UserResponse],
    tags=["用户管理"],
    summary="根据 ID 查询用户",
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: TokenPayload = Depends(get_current_user),   # 需要登录
):
    data = await service.get_by_id(user_id)
    return ResponseModel.ok(data=data)


@router.put(
    "/users/{user_id}",
    response_model=ResponseModel[UserResponse],
    tags=["用户管理"],
    summary="修改用户名",
)
async def update_user(
    user_id: int,
    dto: UserUpdate,
    service: UserService = Depends(get_user_service),
    _: TokenPayload = Depends(get_current_user),
):
    data = await service.update(user_id, dto)
    return ResponseModel.ok(data=data, message="用户更新成功")


@router.delete(
    "/users/{user_id}",
    response_model=ResponseModel[bool],
    tags=["用户管理"],
    summary="删除用户",
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: TokenPayload = Depends(get_current_user),
):
    result = await service.delete(user_id)
    return ResponseModel.ok(data=result, message="用户删除成功")


@router.get(
    "/users",
    response_model=ResponseModel[List[UserResponse]],
    tags=["用户管理"],
    summary="查询所有用户（不分页）",
)
async def list_users(
    service: UserService = Depends(get_user_service),
    _: TokenPayload = Depends(get_current_user),
):
    data = await service.list_all()
    return ResponseModel.ok(data=data)


# ================================================================== #
#  扩展接口
# ================================================================== #

@router.get(
    "/users/page/list",
    response_model=ResponseModel[PageResult[UserResponse]],
    tags=["用户管理"],
    summary="分页查询用户",
    description="支持按 user_name 模糊搜索，返回分页结构。",
)
async def page_query(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页条数"),
    keyword: str = Query(default=None, description="用户名模糊搜索"),
    service: UserService = Depends(get_user_service),
    _: TokenPayload = Depends(get_current_user),
):
    query = UserPageQuery(page=page, page_size=page_size, keyword=keyword)
    data = await service.page_query(query)
    return ResponseModel.ok(data=data)


@router.get(
    "/users/name/{user_name}",
    response_model=ResponseModel[UserResponse],
    tags=["用户管理"],
    summary="根据用户名精确查询",
)
async def get_by_username(
    user_name: str,
    service: UserService = Depends(get_user_service),
    _: TokenPayload = Depends(get_current_user),
):
    data = await service.get_by_username(user_name)
    return ResponseModel.ok(data=data)


@router.patch(
    "/users/{user_id}/password",
    response_model=ResponseModel[bool],
    tags=["用户管理"],
    summary="修改密码",
    description="传入原密码和新密码，校验原密码正确后更新。",
)
async def change_password(
    user_id: int,
    dto: ChangePasswordRequest,
    service: UserService = Depends(get_user_service),
    current_user: TokenPayload = Depends(get_current_user),
):
    # 只允许修改自己的密码
    if str(user_id) != current_user.sub:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="只能修改自己的密码")
    result = await service.change_password(user_id, dto)
    return ResponseModel.ok(data=result, message="密码修改成功")


@router.delete(
    "/users/batch/delete",
    response_model=ResponseModel[int],
    tags=["用户管理"],
    summary="批量删除用户",
    description="传入 user_id 列表，返回成功删除数量。",
)
async def batch_delete(
    ids: List[int],
    service: UserService = Depends(get_user_service),
    _: TokenPayload = Depends(get_current_user),
):
    count = await service.batch_delete(ids)
    return ResponseModel.ok(data=count, message=f"成功删除 {count} 个用户")