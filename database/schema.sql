-- ============================================================================
-- Temu 选品系统 - 数据库表结构初始化脚本
-- ============================================================================
-- 说明：此脚本用于创建 Temu 选品系统所需的数据库表结构
-- 使用方法：
--   1. 创建数据库：CREATE DATABASE temu_products;
--   2. 执行此脚本：psql -U postgres -d temu_products -f schema.sql
-- ============================================================================

-- ============================================================================
-- 表 1: product_main（商品主表）
-- 说明：存储商品的基本信息和最新统计数据
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_main (
    -- 商品基本信息
    product_id VARCHAR(20) PRIMARY KEY,           -- 商品ID
    link TEXT NOT NULL,                           -- 商品链接
    product_title VARCHAR(500) NOT NULL,          -- 商品标题
    image_url TEXT,                               -- 图片链接

    -- 分类信息
    category_level1 VARCHAR(100) NOT NULL,        -- 一级类目
    category_level2 VARCHAR(100) NOT NULL,        -- 二级类目
    ranking_list VARCHAR(50) NOT NULL,            -- 榜单（畅销榜/新品榜）
    shop_type VARCHAR(50) NOT NULL,               -- 店铺类型（全托管/半托管）

    -- 排名信息
    level1_ranking INTEGER DEFAULT 9999,          -- 一级类目排名
    level2_ranking INTEGER DEFAULT 9999,          -- 二级类目排名

    -- 最新数据统计
    latest_date DATE NOT NULL,                    -- 最新数据采集日期
    price NUMERIC NOT NULL,                       -- 价格
    daily_sales INTEGER NOT NULL DEFAULT 0,       -- 日销量
    total_sales INTEGER NOT NULL DEFAULT 0,       -- 总销量
    comment_count INTEGER NOT NULL DEFAULT 0,     -- 评论数

    -- 计算指标
    review_rate NUMERIC DEFAULT 0.0000,           -- 留评率（百分比）
    avg_daily_sales_7d INTEGER DEFAULT 0,         -- 7天平均日销量
    monitor_count INTEGER DEFAULT 1,              -- 监控次数（有多少天的数据）

    -- 调研标记
    is_investigated SMALLINT DEFAULT 0            -- 是否已调研（0=未调研，1=已调研）
);

-- ============================================================================
-- 表 2: product_history（商品历史数据表）
-- 说明：存储商品的历史数据，用于趋势分析
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_history (
    id SERIAL PRIMARY KEY,                        -- 自增主键
    product_id VARCHAR(20) NOT NULL,              -- 商品ID
    collect_date DATE NOT NULL,                   -- 数据采集日期

    -- 历史数据
    price NUMERIC NOT NULL,                       -- 价格
    daily_sales INTEGER NOT NULL DEFAULT 0,       -- 日销量
    total_sales INTEGER NOT NULL DEFAULT 0,       -- 总销量
    comment_count INTEGER NOT NULL DEFAULT 0,     -- 评论数
    level1_ranking INTEGER,                       -- 一级类目排名
    level2_ranking INTEGER,                       -- 二级类目排名

    -- 约束：同一商品在同一天只能有一条记录
    UNIQUE(product_id, collect_date)
);

-- ============================================================================
-- 表 3: raw_products（原始数据表）
-- 说明：存储从数据源采集的原始数据
-- ============================================================================
CREATE TABLE IF NOT EXISTS raw_products (
    id SERIAL PRIMARY KEY,                        -- 自增主键
    collect_date DATE NOT NULL,                   -- 数据采集日期
    product_id BIGINT NOT NULL,                   -- 商品ID
    price NUMERIC NOT NULL,                       -- 价格
    link TEXT NOT NULL,                           -- 商品链接
    shop_type VARCHAR(50),                        -- 店铺类型
    product_title VARCHAR(1000) NOT NULL,         -- 商品标题
    category_level1 VARCHAR(100) NOT NULL,        -- 一级类目
    category_level2 VARCHAR(100) NOT NULL,        -- 二级类目
    total_sales INTEGER DEFAULT 0,                -- 总销量
    category VARCHAR(50),                         -- 类目（旧字段）
    comment_count INTEGER DEFAULT 0,              -- 评论数
    daily_sales INTEGER DEFAULT 0,                -- 日销量
    ranking INTEGER DEFAULT 9999,                 -- 排名
    us_ratio NUMERIC,                             -- 美国占比
    image_url TEXT,                               -- 图片链接
    import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 导入时间
);

-- ============================================================================
-- 创建索引（提升查询性能）
-- ============================================================================

-- 商品主表索引
CREATE INDEX IF NOT EXISTS idx_main_latest_date ON product_main(latest_date);
CREATE INDEX IF NOT EXISTS idx_main_category ON product_main(category_level1, category_level2);
CREATE INDEX IF NOT EXISTS idx_main_ranking_list ON product_main(ranking_list);
CREATE INDEX IF NOT EXISTS idx_main_shop_type ON product_main(shop_type);
CREATE INDEX IF NOT EXISTS idx_main_total_sales ON product_main(total_sales DESC);
CREATE INDEX IF NOT EXISTS idx_main_daily_sales ON product_main(daily_sales DESC);

-- 商品历史表索引
CREATE INDEX IF NOT EXISTS idx_history_product_date ON product_history(product_id, collect_date);
CREATE INDEX IF NOT EXISTS idx_history_collect_date ON product_history(collect_date);

-- 原始数据表索引
CREATE INDEX IF NOT EXISTS idx_raw_collect_date ON raw_products(collect_date);
CREATE INDEX IF NOT EXISTS idx_raw_product_id ON raw_products(product_id);
CREATE INDEX IF NOT EXISTS idx_raw_category ON raw_products(category_level1, category_level2);

-- ============================================================================
-- 创建视图（方便查询）
-- ============================================================================

-- 视图：活跃商品（最近30天有数据）
CREATE OR REPLACE VIEW active_products AS
SELECT *
FROM product_main
WHERE latest_date >= CURRENT_DATE - INTERVAL '30 days';

-- 视图：今日数据统计
CREATE OR REPLACE VIEW today_stats AS
SELECT
    COUNT(*) as total_products,
    COUNT(DISTINCT category_level1) as total_categories,
    COUNT(DISTINCT ranking_list) as total_ranking_lists,
    SUM(total_sales) as sum_total_sales,
    AVG(daily_sales) as avg_daily_sales,
    AVG(price) as avg_price
FROM product_main
WHERE latest_date >= CURRENT_DATE - INTERVAL '7 days';

-- 视图：原始数据概览
CREATE OR REPLACE VIEW raw_data_summary AS
SELECT
    collect_date,
    COUNT(*) as record_count,
    COUNT(DISTINCT product_id) as product_count,
    AVG(price) as avg_price,
    SUM(total_sales) as sum_total_sales
FROM raw_products
GROUP BY collect_date
ORDER BY collect_date DESC;

-- ============================================================================
-- 数据库初始化完成
-- ============================================================================

-- 提示信息
SELECT '数据库表结构创建成功！' as status;
SELECT '已创建 3 个表：product_main（商品主表）、product_history（历史表）、raw_products（原始表）' as info;
SELECT '已创建 2 个视图：active_products（活跃商品）、today_stats（今日统计）' as info;
SELECT '已创建 11 个索引，优化查询性能' as info;
