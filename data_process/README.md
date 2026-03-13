# Temu 选品系统 - 数据清洗脚本

## 📁 项目结构

```
data_process/
├── config.py                  # 配置文件
├── main.py                    # 主入口脚本
├── core/                       # 核心清洗逻辑模块
│   ├── __init__.py
│   ├── basic_cleaner.py        # 基础清洗（shop_type、america_rate、去重）
│   ├── daily_sales_cleaner.py  # 日销量清洗（差分法、区间定值法）
│   └── ranking_selector.py     # 榜单优先级处理
├── database/                  # 数据库操作模块
│   ├── __init__.py
│   └── connection.py           # 数据库连接管理
├── utils/                     # 工具函数模块
│   ├── __init__.py
│   └── helpers.py              # 辅助函数（字段映射、数据转换等）
├── raw_data/                  # 存放原始 CSV/Excel 文件
├── logs/                      # 日志文件
└── README.md                  # 本文档
```

---

## 🚀 快速开始

### 安装依赖
```bash
pip install psycopg2-binary pandas openpyxl
```

### 使用方法

**1. 准备数据文件**
- 将 CSV 或 Excel 文件放入 `raw_data/` 文件夹
- 确保文件包含所有必需字段（日期、商品ID、价格等）
- 确保文件中包含 `ranking_list` 列（值为"畅销榜"或"新品榜"）

**2. 运行清洗脚本**
```bash
python main.py raw_data/your_data.csv
```

**3. 查看结果**
- 检查日志文件：`logs/clean_YYYYMMDD_HHMMSS.log`
- 验证数据库：连接数据库查看 product_main 和 product_history 表

---

## 📊 数据库架构

### 表结构

#### 1. product_main（热数据宽表）
- **用途**：前端选品筛选
- **特点**：每个商品一条记录（最新状态）
- **更新方式**：UPSERT（冲突时更新）

#### 2. product_history（冷数据流水表）
- **用途**：商品详情页趋势图
- **特点**：按日期追加历史快照
- **插入方式**：INSERT（冲突时忽略）

#### 3. raw_products（原始数据暂存表）
- **用途**：CSV 导入缓冲区
- **特点**：结构与 CSV 一致
- **生命周期**：导入后可删除

---

## 🔧 清洗算法说明

### 1. 基础清洗

#### shop_type（店铺类型）
- **异常值**：NULL、空字符串、非"全托管"/"半托管"的值
- **算法**：同类目商品的众数推断
- **默认值**："未知"

#### america_rate（美国占比）
- **缺失值**：-1.0
- **算法**：ffill + bfill 填充

#### 去重
- **维度**：(product_id, ranking_list, collect_date)
- **规则**：保留最后一条记录

#### 榜单优先级
- **优先级**：畅销榜 > 新品榜
- **规则**：同一天同一商品在多个榜单时，只保留畅销榜

### 2. daily_sales（日销量）清洗

#### 优先保留规则
- **保留**：daily_sales > 0（原始有效数据）
- **清洗**：daily_sales <= 0 或为空

#### 清洗算法

**首日处理：**
- 第一天数据：daily_sales = 0

**日期差异常：**
- 日期差 <= 0：daily_sales = 5（默认值）

**差分法（total_sales < 10000）：**
```python
daily_sales = (total_sales今天 - total_sales昨天) / 日期差
```

**重要：如果计算结果为负数**
- 业务逻辑：总销量绝对不可能下降
- 原因：数据异常、平台调整、刷单处罚等导致 total_sales 下降
- 处理：将 daily_sales 设为 0，不使用差分结果

**区间定值法（total_sales >= 10000）：**
```python
10,000 - 49,999    → 130
50,000 - 99,999    → 180
100,000 - 149,999  → 250
150,000 - 299,999  → 300
300,000 - 499,999  → 350
500,000+           → 450
```

**上限检查：**
- 确保不超过理论最大日销量

---

## 📝 字段映射关系

| CSV 字段 | 数据库字段 | 说明 |
|---------|-----------|------|
| 日期 | collect_date | 采集日期 |
| 商品ID | product_id | 商品唯一标识 |
| 价格 | price | 元 |
| 链接 | link | 商品链接 |
| 店铺类型 | shop_type | 全托管/半托管 |
| 商品标题 | product_title | 商品名称 |
| 一级类目 | category_level1 | 如：运动与户外 |
| 二级类目 | category_level2 | 如：运动医疗用品 |
| 总销量 | total_sales | 总销量（件） |
| 评论数 | comment_count | 评论数（条） |
| 日销量 | daily_sales | 日销量（件） |
| 排名 | level2_ranking | 二级类目排名 |
| 美国占比 | america_rate | 美国占比（0.5 或 50%） |
| 图片链接 | image_url | 商品图片 |
| ranking_list | ranking_list | 榜单名称 |

**固定值：**
- level1_ranking = 9999（一级类目排名未知）

**计算字段：**
- review_rate = (评论数 / 总销量) × 100
  - 正常范围：0% - 100%
  - 如果评论数 > 总销量，标记为异常数据（review_rate = NULL）
  - 保留2位小数

---

## ⚙️ 配置说明

所有配置项都在 `config.py` 文件中：

```python
# 数据库配置
DB_CONFIG = {...}

# 业务规则配置
VALID_SHOP_TYPES = ['全托管', '半托管']
RANKING_LIST_PRIORITY = {'畅销榜': 1, '新品榜': 2}

# 日销量区间定值
DAILY_SALES_BY_TOTAL = [...]
```

---

## 🛠️ 故障排查

### 常见问题

**Q: 提示"数据库连接失败"**
A: 检查 `config.py` 中的数据库配置是否正确

**Q: 提示"找不到某个字段"**
A: 检查 CSV 文件是否包含所有必需字段，字段名是否正确

**Q: 清洗后数据没有变化**
A: 检查日志文件，查看具体清洗过程的详细信息

---

## 📞 技术支持

如有问题，请检查：
1. CSV 文件格式是否正确
2. 数据库连接是否正常
3. 日志文件中的详细错误信息

---

## 📄 保留的参考文件

- `product_process/` - 原有的清洗算法项目（参考用）
- `product_data_postgres_20260310_114239.sql` - 历史数据备份

**注意：**
- `product_process/` 项目仅作参考，不参与日常运行
- 日常数据清洗使用 `main.py` 脚本
