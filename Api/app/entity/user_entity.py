"""
app/entity/user_entity.py — 用户实体 & DTO

数据库表：users
字段：user_id（主键）、user_name（用户名）、password（bcrypt 哈希密码）
"""
from typing import Optional
from sqlmodel import SQLModel, Field


# ======== 数据库实体 ========

class User(SQLModel, table=True):
    """用户表实体，对应数据库 users 表"""
    __tablename__ = "users"

    user_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="用户主键 ID（自增）",
    )
    user_name: str = Field(
        max_length=50,
        unique=True,
        index=True,
        description="用户名（唯一）",
    )
    password: str = Field(
        description="bcrypt 哈希密码（不可逆加密，禁止返回给前端）",
    )


# ======== 请求 DTO ========

class UserCreate(SQLModel):
    """创建用户 — 请求体"""
    user_name: str = Field(min_length=1, max_length=50, description="用户名")
    password: str = Field(min_length=6, description="登录密码（明文，Service 层自动加密）")


class UserUpdate(SQLModel):
    """更新用户基本信息 — 请求体（字段均可选）"""
    user_name: Optional[str] = Field(default=None, min_length=1, max_length=50, description="新用户名")


class ChangePasswordRequest(SQLModel):
    """修改密码 — 请求体"""
    old_password: str = Field(description="原密码（明文）")
    new_password: str = Field(min_length=6, description="新密码（明文，至少 6 位）")


class LoginRequest(SQLModel):
    """登录 — 请求体"""
    user_name: str = Field(description="用户名")
    password: str = Field(description="密码（明文）")


# ======== 响应 DTO ========

class UserResponse(SQLModel):
    """用户响应体（不含 password）"""
    user_id: int
    user_name: str

    class Config:
        from_attributes = True


class LoginResponse(SQLModel):
    """登录成功响应体"""
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse


# ======== 分页查询参数 ========

class UserPageQuery(SQLModel):
    """分页 + 关键词查询参数"""
    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(default=10, ge=1, le=100, description="每页条数，最大 100")
    keyword: Optional[str] = Field(default=None, description="用户名关键词模糊搜索")