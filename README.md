# Temu 选品系统

基于 PostgreSQL + FastAPI + Vue 3 的商品选品数据分析系统，支持双表架构、实时数据展示和趋势分析。

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [数据库配置](#数据库配置)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

## 项目简介

本系统用于 Temu 平台商品数据的采集、清洗、存储和可视化分析，提供：
- 📊 实时商品数据展示
- 📈 销量趋势分析
- 🔍 多维度商品筛选
- 📑 双表架构设计（商品表 + 元数据表）

## 技术栈

### 后端
- **FastAPI** - 现代化的 Python Web 框架
- **PostgreSQL** - 关系型数据库
- **psycopg2** - PostgreSQL 数据库适配器
- **Uvicorn** - ASGI 服务器

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 组件库
- **Axios** - HTTP 客户端
- **ECharts** - 数据可视化图表库

### 数据处理
- **Pandas** - 数据分析与处理
- **NumPy** - 科学计算库

## 环境要求

在开始之前，请确保您的开发环境已安装以下软件：

### 必需软件

1. **Python** (版本 3.8+)
   - 下载地址：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **Node.js** (版本 16+)
   - 下载地址：https://nodejs.org/
   - 包含 npm 包管理器

3. **PostgreSQL** (版本 12+)
   - 下载地址：https://www.postgresql.org/download/
   - 安装时记住设置的密码（默认用户：postgres）

4. **Git** (版本控制)
   - 下载地址：https://git-scm.com/downloads

### 可选软件

- **VS Code** - 推荐的代码编辑器
  - 下载地址：https://code.visualstudio.com/

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/temu_selection_system.git
cd temu_selection_system
```

### 2. 数据库配置

#### 方式一：使用提供的 SQL 文件（推荐）

1. 创建数据库：
```sql
CREATE DATABASE temu_products;
```

2. 导入数据表和初始数据：
```bash
# 在 PostgreSQL 命令行或 pgAdmin 中执行
psql -U postgres -d temu_products -f product_data_postgres_20260310_114239.sql
```

#### 方式二：手动创建表结构

参考 `product_data_postgres_20260310_114239.sql` 文件中的表结构定义。

### 3. 配置环境变量

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，修改数据库配置：
```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=temu_products
DB_USER=postgres
DB_PASSWORD=你的数据库密码
```

3. 更新数据库配置文件：
编辑 `data_process/config.py`，修改 `DB_CONFIG` 字典中的数据库连接信息。

### 4. 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

如果 `requirements.txt` 不存在，手动安装：
```bash
pip install fastapi uvicorn psycopg2-binary pandas numpy
```

#### 前端依赖
```bash
cd frontend
npm install
```

### 5. 启动项目

#### 方式一：一键启动（Windows）

双击项目根目录下的 `start.bat` 文件。

#### 方式二：手动启动

**启动后端（终端1）：**
```bash
cd backend
python main.py
```

**启动前端（终端2）：**
```bash
cd frontend
npm run dev
```

### 6. 访问应用

- **前端界面**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 数据库配置

### 数据库迁移

团队成员首次拉取项目后，需要执行以下步骤：

1. **创建数据库**
```sql
CREATE DATABASE temu_products;
```

2. **导入表结构和数据**
```bash
# Windows (在 PostgreSQL 安装目录的 bin 文件夹下)
psql -U postgres -d temu_products -f "C:\path\to\product_data_postgres_20260310_114239.sql"

# Linux/Mac
psql -U postgres -d temu_products -f product_data_postgres_20260310_114239.sql
```

3. **验证数据库连接**
```bash
cd backend
python -c "from database import db_pool; db_pool.init_pool(); print('Database connected successfully!')"
```

### 数据库表说明

- **products** - 商品主表，存储商品基本信息和实时数据
- **product_metadata** - 商品元数据表，存储商品的类别、榜单等元信息

## 项目结构

```
temu_selection_system/
├── backend/                    # 后端 API 服务
│   ├── routers/               # API 路由
│   │   ├── products.py        # 商品相关接口
│   │   └── metadata.py        # 元数据相关接口
│   ├── crud.py                # 数据库操作层
│   ├── database.py            # 数据库连接管理
│   ├── models.py              # 数据模型
│   ├── main.py                # FastAPI 应用入口
│   └── requirements.txt       # Python 依赖列表
├── frontend/                   # 前端应用
│   ├── src/                   # 源代码
│   ├── public/                # 静态资源
│   ├── package.json           # Node 依赖配置
│   └── vite.config.js         # Vite 构建配置
├── data_process/               # 数据处理模块
│   ├── config.py              # 配置文件
│   └── ...                    # 数据处理脚本
├── product_data_postgres_20260310_114239.sql  # 数据库表结构和初始数据
├── start.bat                   # Windows 一键启动脚本
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略文件配置
└── README.md                  # 项目说明文档
```

## 开发指南

### 局域网访问配置

如果需要在局域网内访问，修改以下配置：

1. **后端配置** (`backend/main.py`):
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. **前端配置** (`frontend/vite.config.js`):
```javascript
server: {
  host: '0.0.0.0',
  port: 5173
}
```

3. **防火墙配置**: 确保防火墙允许端口 8000 和 5173

### API 接口文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 API 文档（Swagger UI）。

### 常用命令

```bash
# 后端
cd backend
python main.py                    # 启动后端服务
pip freeze > requirements.txt     # 导出依赖

# 前端
cd frontend
npm run dev                       # 启动开发服务器
npm run build                     # 构建生产版本
npm run preview                   # 预览生产构建

# 数据库
psql -U postgres -d temu_products  # 连接数据库
\dt                               # 查看所有表
\q                                # 退出
```

## 常见问题

### 1. 数据库连接失败

**问题**: `connection refused` 或 `password authentication failed`

**解决方案**:
- 检查 PostgreSQL 服务是否启动
- 确认 `data_process/config.py` 中的数据库密码是否正确
- 检查数据库名称 `temu_products` 是否存在

### 2. 前端无法连接后端 API

**问题**: `Network Error` 或 `CORS error`

**解决方案**:
- 确认后端服务已启动（访问 http://localhost:8000/health）
- 检查 `backend/main.py` 中的 CORS 配置
- 检查前端 API 基础 URL 配置

### 3. 依赖安装失败

**问题**: `pip install` 或 `npm install` 报错

**解决方案**:
```bash
# Python 依赖问题
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# Node 依赖问题
npm cache clean --force
npm install
```

### 4. 端口被占用

**问题**: `Address already in use`

**解决方案**:
```bash
# Windows: 查找并终止占用端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# Linux/Mac:
lsof -i :8000
kill -9 <进程ID>
```

## 团队协作注意事项

1. **不要提交敏感信息**:
   - 数据库密码
   - API 密钥
   - 个人配置文件

2. **提交前检查**:
   - 运行代码格式化工具
   - 确保没有调试代码
   - 测试基本功能是否正常

3. **代码规范**:
   - Python 遵循 PEP 8 规范
   - JavaScript 使用 ESLint 配置
   - 提交信息清晰明确

## 许可证

本项目仅供内部使用。

## 联系方式

如有问题，请联系项目维护者。
