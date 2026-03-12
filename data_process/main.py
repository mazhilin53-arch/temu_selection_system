#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
每日数据清洗主脚本（模块化版本）
功能：导入 CSV → 清洗 → 入库到 product_main + product_history

使用方法：
    python main.py your_data.csv
    python main.py your_data.xlsx
"""

import sys
import os
import pandas as pd
import logging

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import DB_CONFIG, LEVEL1_RANKING_DEFAULT
from core import BasicCleaner, DailySalesCleaner, RankingSelector
from database import DatabaseConnection
from utils import load_csv, map_columns, parse_america_rate, calculate_review_rate
from psycopg2.extras import execute_batch


def setup_logging():
    """设置日志"""
    import datetime

    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = f"{log_dir}/clean_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)


class DataCleaner:
    """数据清洗器"""

    def __init__(self, logger):
        self.logger = logger

        # 初始化组件
        self.db = DatabaseConnection()
        self.basic_cleaner = BasicCleaner(logger)
        self.daily_sales_cleaner = DailySalesCleaner(logger, self.db.get_connection())
        self.ranking_selector = RankingSelector(logger)

        # 缓存
        self.avg_daily_sales_cache = {}
        self.monitor_count_cache = {}

    def clean(self, csv_file_path):
        """执行完整清洗流程"""
        self.logger.info("=" * 80)
        self.logger.info("每日数据清洗程序启动")
        self.logger.info("=" * 80)
        self.logger.info(f"输入文件: {csv_file_path}")

        try:
            # 1. 读取数据
            df = self._load_data(csv_file_path)

            # 2. 基础清洗
            df = self._basic_clean(df)

            # 3. 日销量清洗
            df = self._clean_daily_sales(df)

            # 4. 数据入库
            self._save_to_database(df)

            # 5. 验证结果
            self._verify_results()

            self.logger.info("\n" + "=" * 80)
            self.logger.info("数据清洗完成！")
            self.logger.info("=" * 80)

            return 0

        except Exception as e:
            self.logger.error(f"\n数据清洗失败: {e}")
            import traceback
            traceback.print_exc()
            return 1

        finally:
            self.db.close()

    def _load_data(self, file_path):
        """步骤1：读取数据"""
        self.logger.info("\n步骤1：读取数据...")
        df = load_csv(file_path)
        self.logger.info(f"✓ 读取到 {len(df)} 行数据，{len(df.columns)} 列")
        return df

    def _basic_clean(self, df):
        """步骤2：基础清洗和格式转换"""
        self.logger.info("\n步骤2：基础清洗和格式转换...")

        # 字段映射
        df = map_columns(df)
        self.logger.info("  ✓ 字段映射完成")

        # 转换 america_rate 格式
        df['america_rate'] = df['america_rate'].apply(parse_america_rate)
        self.logger.info("  ✓ america_rate 格式转换完成")

        # 基础清洗（shop_type、america_rate、去重、榜单选择）
        df = self.basic_cleaner.clean_all(df)
        df = self.ranking_selector.select(df)

        self.logger.info("✓ 基础清洗完成")
        return df

    def _clean_daily_sales(self, df):
        """步骤3：日销量清洗"""
        self.logger.info("\n步骤3：日销量清洗...")
        df = self.daily_sales_cleaner.clean(df)
        return df

    def _save_to_database(self, df):
        """步骤4：数据入库"""
        self.logger.info("\n步骤4：数据入库...")

        conn = self.db.get_connection()
        cur = conn.cursor()

        # 4.1 更新 product_main（UPSERT）
        self._update_product_main(cur, df)
        self.logger.info("  ✓ product_main 更新完成")

        # 4.2 更新 product_history（INSERT）
        self._update_product_history(cur, df)
        self.logger.info("  ✓ product_history 更新完成")

        conn.commit()
        cur.close()

    def _calculate_avg_daily_sales_7d(self, cur, product_id):
        """计算最近7次记录的平均日销量"""
        # 检查缓存
        if product_id in self.avg_daily_sales_cache:
            return self.avg_daily_sales_cache[product_id]

        # 查询最近7次记录
        query = """
        SELECT daily_sales
        FROM product_history
        WHERE product_id = %s
        ORDER BY collect_date DESC
        LIMIT 7
        """
        cur.execute(query, (product_id,))
        results = cur.fetchall()

        # 提取日销量列表
        sales_list = [row[0] for row in results]

        # 过滤：只计算 > 0 的值
        non_zero_sales = [s for s in sales_list if s > 0]

        # 计算平均值
        if len(non_zero_sales) == 0:
            avg_sales = 0  # 全是0，返回0
        else:
            # 有几次算几次，最少1次
            avg_sales = int(round(sum(non_zero_sales) / len(non_zero_sales)))

        # 缓存结果
        self.avg_daily_sales_cache[product_id] = avg_sales

        return avg_sales

    def _calculate_monitor_count(self, cur, product_id):
        """
        计算商品的监控次数（在 product_history 中的记录数）

        monitor_count = product_history 表中该商品有多少天的历史数据
        """
        # 检查缓存
        if product_id in self.monitor_count_cache:
            return self.monitor_count_cache[product_id]

        # 统计该商品在 product_history 中的历史记录数
        query = """
        SELECT COUNT(*)
        FROM product_history
        WHERE product_id = %s
        """
        cur.execute(query, (product_id,))
        monitor_count = cur.fetchone()[0]

        # 缓存结果
        self.monitor_count_cache[product_id] = monitor_count

        return monitor_count

    def _update_product_main(self, cur, df):
        """更新到 product_main"""
        upsert_sql = """
        INSERT INTO product_main (
            product_id, link, product_title, image_url,
            category_level1, category_level2, ranking_list, shop_type,
            latest_date, price, daily_sales, total_sales, comment_count,
            level1_ranking, level2_ranking, review_rate,
            avg_daily_sales_7d, monitor_count, is_investigated
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (product_id) DO UPDATE SET
            link = EXCLUDED.link,
            product_title = EXCLUDED.product_title,
            image_url = EXCLUDED.image_url,
            category_level1 = EXCLUDED.category_level1,
            category_level2 = EXCLUDED.category_level2,
            ranking_list = EXCLUDED.ranking_list,
            shop_type = EXCLUDED.shop_type,
            latest_date = EXCLUDED.latest_date,
            price = EXCLUDED.price,
            daily_sales = EXCLUDED.daily_sales,
            total_sales = EXCLUDED.total_sales,
            comment_count = EXCLUDED.comment_count,
            level1_ranking = EXCLUDED.level1_ranking,
            level2_ranking = EXCLUDED.level2_ranking,
            review_rate = EXCLUDED.review_rate,
            avg_daily_sales_7d = EXCLUDED.avg_daily_sales_7d,
            monitor_count = EXCLUDED.monitor_count,
            is_investigated = EXCLUDED.is_investigated
        """

        records = []
        anomaly_count = 0  # 异常数据计数

        for _, row in df.iterrows():
            product_id = str(row['product_id'])
            total_sales = int(row['total_sales']) if pd.notna(row['total_sales']) else 0
            comment_count = int(row['comment_count']) if pd.notna(row['comment_count']) else 0

            # 计算留评率
            review_rate = calculate_review_rate(total_sales, comment_count)

            # 检测异常：评论数 > 总销量
            if review_rate is None and comment_count > total_sales and total_sales > 0:
                anomaly_count += 1
                self.logger.warning(
                    f"    ⚠ 数据异常: 商品 {product_id} | "
                    f"总销量 {total_sales} < 评论数 {comment_count} | "
                    f"留评率设为 NULL"
                )

            record = (
                product_id,
                str(row['link']),
                str(row['product_title']),
                str(row['image_url']) if pd.notna(row['image_url']) else None,
                str(row['category_level1']),
                str(row['category_level2']),
                str(row['ranking_list']),
                str(row['shop_type']),
                row['collect_date'],
                float(row['price']),
                int(row['daily_sales']) if pd.notna(row['daily_sales']) else 0,
                total_sales,
                comment_count,
                LEVEL1_RANKING_DEFAULT,
                int(row['level2_ranking']) if pd.notna(row['level2_ranking']) else 9999,
                review_rate,  # 可能是 None（异常数据）
                self._calculate_avg_daily_sales_7d(cur, product_id),  # 计算近7次平均
                self._calculate_monitor_count(cur, product_id),  # 计算监控次数
                0   # is_investigated 暂时设为0
            )
            records.append(record)

        if anomaly_count > 0:
            self.logger.warning(f"    ⚠ 发现 {anomaly_count} 条留评率异常数据（评论数 > 总销量）")

        execute_batch(cur, upsert_sql, records, page_size=1000)
        self.logger.info(f"    更新 {len(records)} 条记录")

    def _update_product_history(self, cur, df):
        """更新到 product_history"""
        insert_sql = """
        INSERT INTO product_history (
            product_id, collect_date, price, daily_sales,
            total_sales, comment_count, level1_ranking, level2_ranking
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (product_id, collect_date) DO NOTHING
        """

        records = []
        for _, row in df.iterrows():
            record = (
                str(row['product_id']),
                row['collect_date'],
                float(row['price']),
                int(row['daily_sales']) if pd.notna(row['daily_sales']) else 0,
                int(row['total_sales']) if pd.notna(row['total_sales']) else 0,
                int(row['comment_count']) if pd.notna(row['comment_count']) else 0,
                LEVEL1_RANKING_DEFAULT,
                int(row['level2_ranking']) if pd.notna(row['level2_ranking']) else 9999,
            )
            records.append(record)

        execute_batch(cur, insert_sql, records, page_size=1000)
        self.logger.info(f"    追加 {len(records)} 条记录")

    def _verify_results(self):
        """步骤5：验证结果"""
        self.logger.info("\n步骤5：验证结果...")

        conn = self.db.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM product_main")
        main_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM product_history")
        history_count = cur.fetchone()[0]

        cur.close()

        self.logger.info(f"  product_main: {main_count:,} 条")
        self.logger.info(f"  product_history: {history_count:,} 条")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python main.py <csv_file_path>")
        print("示例: python main.py ../raw_data/2026-03-10_畅销榜.csv")
        sys.exit(1)

    csv_file = sys.argv[1]

    # 设置日志
    logger = setup_logging()

    # 执行清洗
    cleaner = DataCleaner(logger)
    exit(cleaner.clean(csv_file))


if __name__ == '__main__':
    main()
