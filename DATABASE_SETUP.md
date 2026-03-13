# 数据库配置指南

## 快速设置

### 1. 安装 PostgreSQL

#### Windows
1. 下载 PostgreSQL 安装程序：https://www.postgresql.org/download/windows/
2. 运行安装程序，记住设置的密码（默认用户名：postgres）
3. 安装完成后，打开 pgAdmin 或命令行工具

#### macOS
```bash
# 使用 Homebrew 安装
brew install postgresql@14
brew services start postgresql@14
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. 创建数据库

#### 方式一：使用 pgAdmin（图形界面）
1. 打开 pgAdmin
2. 右键点击 "Databases" → "Create" → "Database"
3. 输入数据库名称：`temu_products`
4. 点击 "Save"

#### 方式二：使用命令行
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

### 3. 导入数据

#### 使用 psql 命令行
```bash
# Windows
psql -U postgres -d temu_products -f "C:\path\to\product_data_postgres_20260310_114239.sql"

# Linux/Mac
psql -U postgres -d temu_products -f product_data_postgres_20260310_114239.sql
```

#### 使用 pgAdmin
1. 打开 pgAdmin
2. 连接到 PostgreSQL 服务器
3. 选择 `temu_products` 数据库
4. 点击 "Tools" → "Query Tool"
5. 打开 `product_data_postgres_20260310_114239.sql` 文件
6. 点击执行按钮（▶️）

### 4. 配置应用连接

编辑 `data_process/config.py` 文件：

```python
DB_CONFIG = {
    'host': '127.0.0.1',      # 或 'localhost'
    'port': 5432,              # PostgreSQL 默认端口
    'database': 'temu_products',
    'user': 'postgres',        # 您的 PostgreSQL 用户名
    'password': 'your_password'  # 您的数据库密码
}
```

### 5. 测试连接

```bash
cd backend
python -c "from database import db_pool; db_pool.init_pool(); print('✅ 数据库连接成功！')"
```

如果看到 "✅ 数据库连接成功！"，说明配置正确。

## 常见问题

### Q: 忘记 PostgreSQL 密码怎么办？

#### Windows
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

#### Linux/Mac
```bash
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'new_password';
\q
```

### Q: 端口 5432 被占用怎么办？

1. 检查占用端口的进程：
```bash
# Windows
netstat -ano | findstr :5432

# Linux/Mac
lsof -i :5432
```

2. 如果是其他服务占用，可以：
   - 停止该服务
   - 或修改 PostgreSQL 配置使用其他端口

### Q: 如何备份数据库？

```bash
# 备份
pg_dump -U postgres temu_products > backup_$(date +%Y%m%d).sql

# 恢复
psql -U postgres -d temu_products < backup_20260312.sql
```

### Q: 如何查看数据库内容？

```bash
# 连接数据库
psql -U postgres -d temu_products

# 查看所有表
\dt

# 查看表结构
\d products

# 查询数据
SELECT * FROM products LIMIT 10;

# 退出
\q
```

## 数据库表结构

### products（商品主表）
| 字段 | 类型 | 说明 |
|------|------|------|
| product_id | VARCHAR(50) | 商品ID（主键） |
| collect_date | DATE | 采集日期 |
| price | DECIMAL | 价格 |
| total_sales | INTEGER | 总销量 |
| daily_sales | INTEGER | 日销量 |
| comment_count | INTEGER | 评论数 |
| america_rate | DECIMAL | 美国占比 |

### product_metadata（商品元数据表）
| 字段 | 类型 | 说明 |
|------|------|------|
| product_id | VARCHAR(50) | 商品ID（主键） |
| product_title | TEXT | 商品标题 |
| link | TEXT | 商品链接 |
| image_url | TEXT | 图片链接 |
| category_level1 | VARCHAR(100) | 一级类目 |
| category_level2 | VARCHAR(100) | 二级类目 |
| shop_type | VARCHAR(20) | 店铺类型 |
| ranking_list | VARCHAR(50) | 榜单 |
| level1_ranking | INTEGER | 一级排名 |
| level2_ranking | INTEGER | 二级排名 |

## 性能优化建议

1. **创建索引**
```sql
-- 在商品ID上创建索引
CREATE INDEX idx_product_id ON products(product_id);

-- 在日期上创建索引
CREATE INDEX idx_collect_date ON products(collect_date);

-- 在类目上创建索引
CREATE INDEX idx_category ON product_metadata(category_level2);
```

2. **定期清理旧数据**
```sql
-- 删除30天前的数据
DELETE FROM products WHERE collect_date < CURRENT_DATE - INTERVAL '30 days';
```

3. **定期分析表**
```sql
ANALYZE products;
ANALYZE product_metadata;
```

## 安全建议

1. **不要将数据库密码提交到 Git**
   - 使用 `.env` 文件存储敏感信息
   - `.env` 文件已在 `.gitignore` 中

2. **限制数据库访问权限**
   - 为应用创建专用数据库用户
   - 只授予必要的权限

3. **定期备份数据**
   - 设置自动备份任务
   - 保留多个时间点的备份

## 联系支持

如果遇到问题，请联系项目维护者。
