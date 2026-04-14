# 新 GET 方法测试指南

## 新增端点

您已经在 User Controller 中添加了一个使用其他数据库连接的 GET 方法：

### 端点信息
- **方法**: GET
- **路由**: `/api/v1/users/other-db/{user_id}`
- **认证**: 需要 Bearer Token（需要先登录）
- **标签**: 用户管理
- **描述**: 从其他库（如分析库、日志库、审计库）查询用户数据

---

## 使用步骤

### 1️⃣ 登录获取 Token

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "admin",
    "password": "password123"
  }'
```

**响应示例**：
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "user": {
      "user_id": 1,
      "user_name": "admin"
    }
  }
}
```

### 2️⃣ 使用 Token 调用新端点

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/users/other-db/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**响应示例**：
```json
{
  "code": 0,
  "message": "查询成功",
  "data": {
    "source": "other_database",
    "user_id": 1,
    "user_name": "admin",
    "message": "从其他库成功查询到数据"
  }
}
```

---

## 通过 Swagger UI 测试

1. 打开 http://127.0.0.1:8000/docs
2. 在左上角找到 `Authorize` 按钮
3. 在登录接口中获取 `access_token`
4. 点击 `Authorize` 按钮，粘贴 Token
5. 找到新增的 `GET /api/v1/users/other-db/{user_id}` 端点
6. 点击 `Try it out`，输入 `user_id`
7. 点击 `Execute` 执行

---

## 后端工作原理

此方法展示了如何使用多数据库连接：

```python
@router.get("/users/other-db/{user_id}")
async def get_user_from_other_db(
    user_id: int,
    session_other: Session = Depends(get_session_other),  # ✅ 使用其他库连接
    _: TokenPayload = Depends(get_current_user),
):
    # 从其他库查询用户数据
    stmt = select(User).where(User.user_id == user_id)
    user = session_other.exec(stmt).first()
    # 返回查询结果
    ...
```

### 关键点：
- ✅ 使用 `get_session_other()` 注入其他库的 Session
- ✅ 需要 JWT Token 认证（`get_current_user` 依赖）
- ✅ 返回 `ResponseModel[dict]` 格式
- ✅ 包含异常处理

---

## 配置说明

其他库的连接配置在 `app/core/config.py` 中：

```python
# 其他数据库配置（如分析库、日志库等）
OTHER_DB_NAME = "test"
OTHER_DB_USER = "root"
OTHER_DB_PASSWORD = "123456"
OTHER_DB_HOST = "localhost"
OTHER_DB_PORT = "3306"

DATABASE_OTHER_URL = f"mysql+pymysql://{OTHER_DB_USER}:{OTHER_DB_PASSWORD}@{OTHER_DB_HOST}:{OTHER_DB_PORT}/{OTHER_DB_NAME}"
```

根据您的实际需求修改这些配置。

---

## 可能的应用场景

- 📊 从分析库查询用户的统计数据
- 📝 从日志库查询用户的操作历史
- 🔍 从审计库查询用户的变更记录
- 🔐 从安全库查询用户的登录记录
- 💾 跨数据库的数据关联查询

---

## 故障排查

| 问题 | 解决方案 |
|------|--------|
| 401 Unauthorized | 未提供有效的 Bearer Token，请先登录 |
| 403 Forbidden | Token 已过期，请重新登录 |
| 500 Internal Server Error | 检查其他库连接配置是否正确 |
| 其他库连接失败 | 检查 `DATABASE_OTHER_URL` 是否有效 |

