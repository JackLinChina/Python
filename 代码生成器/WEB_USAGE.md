# 🚀 可视化代码生成器 - 使用说明

## 功能特性

✨ **完整的可视化界面**
- Web 界面，跨平台使用（Windows/Mac/Linux）
- 美观的现代化设计
- 实时反馈和进度提示

🗄️ **多数据库支持**
- MySQL
- PostgreSQL
- SQL Server
- Oracle

## 快速开始

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 启动应用

```bash
python app.py
```

然后访问浏览器：
```
http://127.0.0.1:5000
```

## 使用流程

### 第一步：连接数据库
1. 选择数据库类型（MySQL/PostgreSQL/SQL Server/Oracle）
2. 填写连接信息（主机、端口、用户名、密码、数据库名）
3. 点击"🔗 测试连接"按钮

### 第二步：选择表（支持多选）
1. 连接成功后，表列表会自动加载
2. 勾选要生成代码的表（支持同时选择多个表）
3. 主键字段会自动排除，其他字段全部生成

### 第三步：生成代码
1. 点击"✨ 生成代码"按钮
2. 生成完成后，点击"⬇️ 下载代码压缩包"
3. 代码会自动打包为 ZIP 文件并下载到本地
4. 服务器上不会保留任何文件，完全自动清理

## 各数据库的连接配置示例

### MySQL
```
主机: localhost
端口: 3306
用户名: root
密码: (输入密码)
数据库: your_database
```

### PostgreSQL
```
主机: localhost
端口: 5432
用户名: postgres
密码: (输入密码)
数据库: your_database
```
主机: localhost
端口: 1433
用户名: sa
密码: (输入密码)
数据库: your_database
```

### Oracle
```
主机: localhost
端口: 1521
用户名: system
密码: (输入密码)
Service Name: ORCL
```

## 生成的代码结构

生成的代码包括：

```
Api/
├── app/
│   ├── entity/
│   │   └── {table_name}_entity.py    # Entity & DTO 类
│   ├── service/
│   │   └── {table_name}_service.py   # 业务逻辑层
│   ├── controller/
│   │   └── {table_name}_controller.py # 控制层
│   └── dao/
│       └── {table_name}_dao.py        # 数据访问层
```

## 常见问题

### Q: 连接总是失败？
**A:** 请检查：
1. 数据库服务是否正常运行
2. 连接信息是否正确（主机、端口、用户名、密码）
3. 是否有防火墙限制
4. 对应的数据库驱动是否已安装

### Q: 能否只选择某些字段？
**A:** 现在改为自动选择所有非主键字段，无需手动配置。如需自定义，可编辑 [codegen.py](codegen.py) 修改生成逻辑。

### Q: 能否同时生成多个表的代码？
**A:** 支持！可以在第二步选择多个表，系统会依次为每个表生成代码。

### Q: 生成的代码能否自定义？
**A:** 可以！编辑 [codegen.py](codegen.py) 和 [codegen_advanced.py](codegen_advanced.py) 来自定义代码模板。

### Q: 生成的代码是否会保留在服务器上？
**A:** 不会！生成的代码会自动压缩为 ZIP 文件供下载，下载完成后服务器会自动清理所有临时文件。

### Q: 下载的 ZIP 文件中包含什么？
**A:** ZIP 文件包含完整的 Api 文件夹结构，其中包括：
- `entity/{table}_entity.py` - Entity 和 DTO 类
- `service/{table}_service.py` - 业务逻辑层
- `controller/{table}_controller.py` - 控制层
- `dao/{table}_dao.py` - 数据访问层

## 技术栈

- **后端**: Flask + Python
- **前端**: HTML5 + CSS3 + JavaScript
- **数据库驱动**:
  - MySQL: PyMySQL
  - PostgreSQL: psycopg2
  - SQL Server: pyodbc
  - Oracle: cx_Oracle

## 集成建议

### 与现有代码生成器集成

Web 界面已经集成了现有的 `CodeGenerator` 和 `EntityConfig`，可以直接使用现有的代码生成逻辑。

```python
# app.py 中的集成示例
from codegen import CodeGenerator, EntityConfig, FieldConfig

generator = CodeGenerator(output_path)
generator.save_files(config, output_path)
```

## 配置文件

### 修改默认连接参数

编辑 `app.py` 中的连接默认值：

```python
# MySQL 默认端口
'port': int(data.get('port', 3306)),

# PostgreSQL 默认端口
'port': int(data.get('port', 5432))
```

### 自定义代码模板

修改 `codegen.py` 中的代码生成方法来自定义生成的代码风格。

## 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| Enter | 在连接信息输入框中测试连接 |
| Tab | 在字段选择中快速切换 |

## 性能优化建议

- 对于大型数据库（>1000张表），建议分批导入
- 如果连接超时，增加连接超时时间（在 db_reader.py 中配置）
- 大量生成代码时，建议使用后台任务队列

## 反馈与支持

如遇到问题，请检查：
1. Python 版本是否为 3.7+
2. 所有依赖是否正确安装
3. 数据库连接是否正常

## 许可证

MIT License

## 更新日志
### v1.2.0 (2024)
- ✨ **简化工作流** - 移除字段配置步骤
  - 自动选择所有非主键字段
  - 支持多表同时勾选
  - 流程从 4 步简化到 3 步
  - 提升操作效率
### v1.1.0 (2024)
- ✨ **新增功能** - 自动打包下载
  - 生成的代码自动압缩为 ZIP 文件
  - 直接从浏览器下载，无需访问服务器文件系统
  - 下载完成后自动清理服务器临时文件
  - 支持多表批量生成

### v1.0.0 (2024)
- ✨ 初始版本发布
- 🎨 完整的 Web UI
- ✅ 支持 4 种主流数据库
- 🚀 实时数据库表加载
- 📦 自动代码生成
