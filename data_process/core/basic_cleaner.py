#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础清洗模块
处理：shop_type、america_rate、去重
"""

import pandas as pd
from config import VALID_SHOP_TYPES, DEFAULT_SHOP_TYPE, AMERICA_RATE_MISSING


class BasicCleaner:
    """基础清洗器"""

    def __init__(self, logger):
        self.logger = logger

    def clean_all(self, df):
        """
        执行所有基础清洗
        """
        self.logger.info("开始基础清洗...")

        df = self._clean_shop_type(df)
        df = self._clean_america_rate(df)
        df = self._remove_duplicates(df)

        self.logger.info("基础清洗完成")
        return df

    def _clean_shop_type(self, df):
        """
        清洗 shop_type：使用同类目商品的众数推断
        """
        self.logger.info("  清洗 shop_type...")

        abnormal_count = 0

        for idx, row in df.iterrows():
            shop_type = row['shop_type']

            # 检查是否异常
            if pd.isna(shop_type) or shop_type == '' or shop_type not in VALID_SHOP_TYPES:
                # 从同类目商品推断
                same_category = df[
                    (df['category_level1'] == row['category_level1']) &
                    (df['category_level2'] == row['category_level2']) &
                    (df['shop_type'].isin(VALID_SHOP_TYPES))
                ]

                if not same_category.empty:
                    # 使用众数
                    mode_shop_type = same_category['shop_type'].mode()[0]
                    df.at[idx, 'shop_type'] = mode_shop_type
                    abnormal_count += 1
                else:
                    # 无法推断，设为默认值
                    df.at[idx, 'shop_type'] = DEFAULT_SHOP_TYPE

        self.logger.info(f"    shop_type 清洗完成（清洗 {abnormal_count} 条）")
        return df

    def _clean_america_rate(self, df):
        """
        清洗 america_rate：使用 ffill + bfill 填充缺失值
        """
        self.logger.info("  清洗 america_rate...")

        filled_count = 0

        for product_id in df['product_id'].unique():
            mask = df['product_id'] == product_id
            group = df[mask].copy()

            # 缺失值判断
            missing_mask = group['america_rate'] == AMERICA_RATE_MISSING

            if not missing_mask.all() and missing_mask.any():
                # 部分缺失，用 ffill + bfill
                filled_values = group['america_rate'].ffill().bfill()
                df.loc[mask, 'america_rate'] = filled_values.values
                filled_count += missing_mask.sum()

        self.logger.info(f"    america_rate 清洗完成（填充 {filled_count} 条）")
        return df

    def _remove_duplicates(self, df):
        """
        去重：按 (product_id, ranking_list, collect_date) 保留最后一条
        """
        self.logger.info("  去重...")

        original_count = len(df)
        df = df.drop_duplicates(subset=['product_id', 'ranking_list', 'collect_date'], keep='last')
        removed_count = original_count - len(df)

        if removed_count > 0:
            self.logger.info(f"    去重完成（删除 {removed_count} 条重复记录）")
        else:
            self.logger.info("    去重完成（无重复记录）")

        return df
