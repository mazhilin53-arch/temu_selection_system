#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日销量清洗模块
算法：差分法 + 区间定值法
"""

import pandas as pd
from config import (
    DAILY_SALES_BY_TOTAL,
    DEFAULT_DAILY_SALES
)


class DailySalesCleaner:
    """日销量清洗器"""

    def __init__(self, logger, db_connection):
        self.logger = logger
        self.conn = db_connection

    def clean(self, df):
        """
        清洗日销量字段
        逻辑：优先保留原始有效数据（>0），无效数据使用算法计算
        """
        self.logger.info("  清洗 daily_sales...")

        cleaned_count = 0

        for idx, row in df.iterrows():
            daily_sales = row['daily_sales']

            # 保留原始有效数据
            if pd.notna(daily_sales) and daily_sales > 0:
                continue

            # 需要清洗的数据
            product_id = row['product_id']
            collect_date = row['collect_date']
            total_sales = row['total_sales']

            try:
                # 获取历史数据
                history = self._get_history_data(product_id)

                if not history:
                    df.at[idx, 'daily_sales'] = 0
                    continue

                # 找到前一次监测数据
                prev_record = self._find_previous_record(history, collect_date)
                if not prev_record:
                    df.at[idx, 'daily_sales'] = 0
                    continue

                # 计算日期差（确保都是 date 类型）
                if isinstance(collect_date, pd.Timestamp):
                    collect_date = collect_date.date()
                prev_date = prev_record[0]
                if isinstance(prev_date, pd.Timestamp):
                    prev_date = prev_date.date()
                date_diff = (collect_date - prev_date).days

                if date_diff <= 0:
                    df.at[idx, 'daily_sales'] = DEFAULT_DAILY_SALES
                    continue

                prev_total_sales = prev_record[1]

                # 根据当天 total_sales 选择清洗方法
                if total_sales < 10000:
                    # 【差分法】
                    daily_sales_cleaned = self._clean_by_diff_method(
                        total_sales, prev_total_sales, date_diff
                    )
                else:
                    # 【区间定值法】
                    daily_sales_cleaned = self._clean_by_fixed_method(total_sales)

                # 上限检查
                max_daily_sales = self._calc_max_daily_sales(
                    total_sales, prev_total_sales, date_diff
                )
                df.at[idx, 'daily_sales'] = min(daily_sales_cleaned, max_daily_sales)

                cleaned_count += 1

            except Exception as e:
                self.logger.error(f"    daily_sales 清洗失败: {e}")
                continue

        self.logger.info(f"    daily_sales 清洗完成（清洗 {cleaned_count} 条）")
        return df

    def _get_history_data(self, product_id, days_back=7):
        """从 product_history 获取历史数据"""
        cur = self.conn.cursor()
        query = """
        SELECT collect_date, total_sales
        FROM product_history
        WHERE product_id = %s
        ORDER BY collect_date DESC
        LIMIT %s
        """
        # 确保 product_id 是字符串类型（数据库字段是 VARCHAR）
        cur.execute(query, (str(product_id), days_back))
        results = cur.fetchall()
        cur.close()
        return results

    def _find_previous_record(self, history, current_date):
        """在历史数据中找到前一次监测记录"""
        for record in history:
            # 确保 current_date 转换为 date 类型进行比较
            if isinstance(current_date, pd.Timestamp):
                current_date = current_date.date()
            if record[0] < current_date:
                return record
        return None

    def _clean_by_diff_method(self, total_sales, prev_total_sales, days_diff):
        """差分法：总销量 < 10000"""
        total_sale_diff = total_sales - prev_total_sales
        daily_sales = int(round(total_sale_diff / days_diff))

        # 如果总销量下降（差分结果为负），说明是数据异常/平台调整
        # 从业务逻辑上讲，总销量绝对不可能下降
        # 这种情况下直接将日销量设为0，不做差分
        if daily_sales < 0:
            return 0

        return max(daily_sales, 0)

    def _clean_by_fixed_method(self, total_sales):
        """区间定值法：总销量 >= 10000"""
        for min_val, max_val, daily_val in DAILY_SALES_BY_TOTAL:
            if min_val <= total_sales < max_val:
                return daily_val
        return 450  # 默认最高值

    def _calc_max_daily_sales(self, total_sale_current, total_sale_previous, days_diff):
        """计算理论最大日销量"""
        previous_k = int(total_sale_previous / 1000)
        previous_total_sale_min = 1000 * previous_k if previous_k > 0 else total_sale_previous

        current_k = int(total_sale_current / 1000)
        current_total_sale_max = 1000 * (current_k + 1) if current_k > 0 else total_sale_current

        return int(round((current_total_sale_max - previous_total_sale_min) / days_diff))
