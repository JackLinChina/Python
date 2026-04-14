"""
app/core/security.py — 密码加密 & JWT 工具

包含：
  - 密码 bcrypt 哈希 / 校验（直接使用 bcrypt 库，兼容所有版本）
  - JWT access token 生成 / 解析
  - FastAPI 依赖：get_current_user（从请求头解析当前登录用户）
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

# ------------------------------------------------------------------ #
#  密码工具（直接调用 bcrypt，不经过 passlib，兼容 bcrypt 4.x）
# ------------------------------------------------------------------ #

def hash_password(plain: str) -> str:
    """明文密码 → bcrypt 哈希字符串"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与 bcrypt 哈希是否匹配"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ------------------------------------------------------------------ #
#  JWT 工具
# ------------------------------------------------------------------ #

class TokenPayload(BaseModel):
    sub: str          # user_id（字符串形式）
    user_name: str
    exp: Optional[datetime] = None


def create_access_token(user_id: int, user_name: str) -> str:
    """生成 JWT access token"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "user_name": user_name,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    """解析 JWT，失败则抛出 HTTPException 401"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token 无效或已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError:
        raise credentials_exception


# ------------------------------------------------------------------ #
#  FastAPI 依赖：解析当前登录用户
# ------------------------------------------------------------------ #

_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> TokenPayload:
    """
    从 Authorization: Bearer <token> 中解析当前用户信息。
    在需要鉴权的路由上使用：
        current_user: TokenPayload = Depends(get_current_user)
    """
    return decode_access_token(credentials.credentials)