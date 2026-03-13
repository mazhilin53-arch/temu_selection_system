# 数据库团队协作指南

本目录包含用于团队协作的数据库文件，让团队成员可以快速搭建相同的数据库环境。

---

## 📁 文件说明

| 文件名 | 说明 | 大小 |
|--------|------|------|
| `schema.sql` | 数据库表结构定义文件 | ~20 KB |
| `data_dump.sql` | 项目数据导出文件（包含所有商品数据）<br/>**⚠️ 不提交到 Git** | ~167 MB |
| `export_data.py` | 数据导出工具（用于导出最新数据） | ~10 KB |

---

## 🚀 快速开始（团队成员首次使用）

### 第一步：安装 PostgreSQL

确保你的电脑已安装 PostgreSQL（版本 12+）

**Windows:**
- 下载：https://www.postgresql.org/download/windows/
- 安装时记住设置的密码（默认用户名：postgres）

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 第二步：创建数据库

#### 方式一：使用命令行（推荐）

```bash
# Windows (在 PostgreSQL 安装目录的 bin 文件夹下)
psql -U postgres
CREATE DATABASE temu_products;
\q

# Linux/Mac
sudo -u postgres psql
CREATE DATABASE temu_products;
\q
```

#### 方式二：使用 pgAdmin（图形界面）

1. 打开 pgAdmin
2. 右键点击 "Databases" → "Create" → "Database"
3. 输入数据库名称：`temu_products`
4. 点击 "Save"

### 第三步：创建数据表

使用 `schema.sql` 文件创建数据库表结构：

```bash
# Windows
psql -U postgres -d temu_products -f database/schema.sql

# Linux/Mac
psql -U postgres -d temu_products -f database/schema.sql
```

**创建完成后，你将拥有以下3个表：**
- ✅ `product_main` - 商品主表（存储商品最新数据）
- ✅ `product_history` - 商品历史表（存储历史趋势数据）
- ✅ `raw_products` - 原始数据表（存储采集的原始数据）

### 第四步：获取数据导出文件

**⚠️ 重要提示：** `data_dump.sql` 文件太大（~167MB），不提交到 Git 仓库。

**获取方式：**
1. **从项目维护者处获取**：联系项目负责人获取最新的数据文件
2. **自行导出**：如果已有数据库，可以使用导出工具（见下方"导出最新数据"部分）
3. **从网盘/云存储下载**：项目可能将数据文件存储在共享网盘中

将获取的 `data_dump.sql` 文件放到 `database/` 目录下。

### 第五步：导入项目数据

使用 `data_dump.sql` 文件导入所有商品数据：

```bash
# Windows
psql -U postgres -d temu_products -f database/data_dump.sql

# Linux/Mac
psql -U postgres -d temu_products -f database/data_dump.sql
```

**导入完成后，你将拥有：**
- 📊 64,384 条商品数据
- 📈 497,077 条历史记录

### 第六步：验证安装

#### 方式一：使用检查脚本（推荐）

在项目根目录运行：

```bash
python check_schema.py
```

这会显示：
- 数据库中的所有表
- 每个表的完整字段结构
- 字段类型、默认值、约束等详细信息

#### 方式二：手动连接验证

```bash
psql -U postgres -d temu_products
```

然后执行以下 SQL 查询：

```sql
-- 查看所有表
\dt

-- 查看数据统计
SELECT 'product_main' as table_name, COUNT(*) as count FROM product_main
UNION ALL
SELECT 'product_history', COUNT(*) FROM product_history
UNION ALL
SELECT 'raw_products', COUNT(*) FROM raw_products;

-- 查看最新10条商品数据
SELECT product_id, product_title, price, total_sales, latest_date
FROM product_main
ORDER BY total_sales DESC
LIMIT 10;

-- 退出
\q
```

**预期结果：**
```
   table_name    | count
-----------------+--------
 product_main    |  64384
 product_history | 497077
 raw_products    |      0
```

---

## ⚙️ 配置项目连接数据库

导入数据后，需要配置项目连接到数据库：

### 1. 复制环境变量模板

在项目根目录执行：

```bash
cp .env.example .env
```

### 2. 编辑 `.env` 文件

修改数据库配置为你的本地配置：

```env
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=temu_products
DB_USER=postgres
DB_PASSWORD=你的数据库密码

# 后端服务配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 前端服务配置
FRONTEND_PORT=5173
```

### 3. 更新配置文件

编辑 `data_process/config.py`，确保数据库密码正确：

```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'database': 'temu_products',
    'user': 'postgres',
    'password': '你的数据库密码'  # 修改这里
}
```

### 4. 测试连接

```bash
cd backend
python -c "from database import db_pool; db_pool.init_pool(); print('数据库连接成功！')"
```

如果看到 "数据库连接成功！"，说明配置正确。

---

## 📤 导出最新数据（数据更新）

当数据库有新数据时，可以使用导出工具生成最新的 `data_dump.sql`：

### 运行导出脚本

```bash
cd database
python export_data.py
```

### 导出结果

脚本会在 `database/` 目录下生成 `data_dump.sql` 文件，包含：
- `product_main` 表的所有数据
- `product_history` 表的所有数据
- `raw_products` 表的所有数据

### 分享数据

将生成的 `data_dump.sql` 文件：
- 通过网盘、邮件等方式分享给团队成员
- **注意**：不要提交到 Git（文件太大）

---

## 🔧 常见问题

### Q1: 导入数据时出现错误 "database does not exist"

**解决方法：** 先创建数据库
```sql
CREATE DATABASE temu_products;
```

### Q2: 导入数据时提示 "relation already exists"

**解决方法：** 删除现有表重新创建
```sql
DROP TABLE IF EXISTS raw_products CASCADE;
DROP TABLE IF EXISTS product_history CASCADE;
DROP TABLE IF EXISTS product_main CASCADE;
```

然后重新执行 `schema.sql` 和 `data_dump.sql`

### Q3: 忘记 PostgreSQL 密码怎么办？

**Windows:**
1. 打开 "服务" (services.msc)
2. 找到 "postgresql-x64-14" 服务
3. 停止服务
4. 编辑 `pg_hba.conf` 文件（通常在 `C:\Program Files\PostgreSQL\14\data\`）
5. 将 `md5` 改为 `trust`
6. 重启服务
7. 使用空密码连接，然后修改密码：
```sql
ALTER USER postgres WITH PASSWORD 'new_password';
```

**Linux/Mac:**
```bash
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'new_password';
\q
```

### Q4: data_dump.sql 文件太大

**说明：** data_dump.sql 文件不提交到 Git，需要：
- 使用网盘、云存储分享
- 或使用私有文件传输服务
- 团队内部使用压缩文件分享

### Q5: 端口 5432 被占用怎么办？

**检查占用进程：**
```bash
# Windows
netstat -ano | findstr :5432

# Linux/Mac
lsof -i :5432
```

**解决方案：**
- 停止占用端口的进程
- 或修改 PostgreSQL 配置使用其他端口（如 5433）

---

## 📊 数据库表结构说明

### product_main（商品主表）

存储商品的基本信息和最新统计数据

| 字段 | 类型 | 说明 |
|------|------|------|
| product_id | VARCHAR(20) | 商品ID（主键） |
| link | TEXT | 商品链接 |
| product_title | VARCHAR(500) | 商品标题 |
| image_url | TEXT | 图片链接 |
| category_level1 | VARCHAR(100) | 一级类目 |
| category_level2 | VARCHAR(100) | 二级类目 |
| ranking_list | VARCHAR(50) | 榜单（畅销榜/新品榜） |
| shop_type | VARCHAR(50) | 店铺类型（全托管/半托管） |
| level1_ranking | INTEGER | 一级类目排名 |
| level2_ranking | INTEGER | 二级类目排名 |
| latest_date | DATE | 最新数据采集日期 |
| price | NUMERIC | 价格 |
| daily_sales | INTEGER | 日销量 |
| total_sales | INTEGER | 总销量 |
| comment_count | INTEGER | 评论数 |
| review_rate | NUMERIC | 留评率 |
| avg_daily_sales_7d | INTEGER | 7天平均日销量 |
| monitor_count | INTEGER | 监控次数 |
| is_investigated | SMALLINT | 是否已调研 |

### product_history（商品历史表）

存储商品的历史数据，用于趋势分析

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 自增主键 |
| product_id | VARCHAR(20) | 商品ID |
| collect_date | DATE | 数据采集日期 |
| price | NUMERIC | 价格 |
| daily_sales | INTEGER | 日销量 |
| total_sales | INTEGER | 总销量 |
| comment_count | INTEGER | 评论数 |
| level1_ranking | INTEGER | 一级类目排名 |
| level2_ranking | INTEGER | 二级类目排名 |

### raw_products（原始数据表）

存储从数据源采集的原始数据

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 自增主键 |
| collect_date | DATE | 数据采集日期 |
| product_id | BIGINT | 商品ID |
| price | NUMERIC | 价格 |
| link | TEXT | 商品链接 |
| shop_type | VARCHAR(50) | 店铺类型 |
| product_title | VARCHAR(1000) | 商品标题 |
| category_level1 | VARCHAR(100) | 一级类目 |
| category_level2 | VARCHAR(100) | 二级类目 |
| total_sales | INTEGER | 总销量 |
| category | VARCHAR(50) | 类目（旧字段） |
| comment_count | INTEGER | 评论数 |
| daily_sales | INTEGER | 日销量 |
| ranking | INTEGER | 排名 |
| us_ratio | NUMERIC | 美国占比 |
| image_url | TEXT | 图片链接 |
| import_time | TIMESTAMP | 导入时间 |

---

## 💡 提示

1. **定期备份：** 建议定期导出数据备份
   ```bash
   pg_dump -U postgres temu_products > backup_$(date +%Y%m%d).sql
   ```

2. **数据安全：** 不要将包含敏感信息的数据库文件提交到公共仓库

3. **性能优化：** 定期清理旧数据或归档历史数据

4. **团队协作：** 数据更新后及时通知团队成员重新导入

---

## 📞 获取帮助

如果遇到问题，请联系项目维护者。
