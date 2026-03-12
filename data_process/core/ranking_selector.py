#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
榜单选择模块
处理：同一天同一商品在多个榜单时，优先保留畅销榜
"""

import pandas as pd
from config import RANKING_LIST_PRIORITY


class RankingSelector:
    """榜单选择器"""

    def __init__(self, logger):
        self.logger = logger

    def select(self, df):
        """
        选择榜单：如果同一天同一商品在多个榜单，优先保留畅销榜
        """
        self.logger.info("  处理榜单优先级...")

        # 添加优先级列
        df['priority'] = df['ranking_list'].map(
            lambda x: RANKING_LIST_PRIORITY.get(x, 999)
        )

        # 按日期和商品分组
        grouped = df.groupby(['collect_date', 'product_id'])

        kept_records = []
        removed_count = 0

        for (collect_date, product_id), group in grouped:
            if len(group) == 1:
                # 只有一个榜单，直接保留
                kept_records.append(group)
            else:
                # 多个榜单，按优先级排序，保留第一条
                group = group.sort_values('priority')
                kept_records.append(group.head(1))
                removed_count += len(group) - 1

        if removed_count > 0:
            self.logger.info(f"    榜单优先级处理完成（删除 {removed_count} 条低优先级记录）")
        else:
            self.logger.info("    榜单优先级处理完成（无冲突）")

        # 删除临时列并合并结果
        if kept_records:
            result_df = pd.concat(kept_records, ignore_index=True)
            result_df = result_df.drop(columns=['priority'])
            return result_df
        else:
            return df
