"""
main.py — FastAPI 应用入口

启动命令：
  uvicorn main:app --reload

接口文档：
  Swagger UI  → http://localhost:8000/docs
  ReDoc       → http://localhost:8000/redoc
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.controllers.user_controller import router as user_router

# ------------------------------------------------------------------ #
#  创建 FastAPI 实例
# ------------------------------------------------------------------ #

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Python FastAPI 分层架构模板（Entity / IService / Service / Controller）",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------ #
#  中间件
# ------------------------------------------------------------------ #

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
#  全局异常处理器
# ------------------------------------------------------------------ #

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# ------------------------------------------------------------------ #
#  路由注册
# ------------------------------------------------------------------ #

app.include_router(user_router, prefix="/api/v1")

# ------------------------------------------------------------------ #
#  生命周期事件
# ------------------------------------------------------------------ #

@app.on_event("startup")
def on_startup():
    """应用启动时自动建表"""
    create_db_and_tables()


# ------------------------------------------------------------------ #
#  基础路由
# ------------------------------------------------------------------ #

@app.get("/", tags=["健康检查"], summary="根路径")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["健康检查"], summary="健康检查")
async def health():
    return {"status": "ok"}