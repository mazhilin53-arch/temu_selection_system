#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具函数模块
"""

import pandas as pd
from config import COLUMN_MAPPING, LEVEL1_RANKING_DEFAULT, AMERICA_RATE_MISSING


def parse_america_rate(value):
    """转换美国占比：'50%' → 0.5, '0.5' → 0.5"""
    if pd.isna(value):
        return AMERICA_RATE_MISSING

    value = str(value).strip()

    if value == '-1' or value == '-1.0':
        return AMERICA_RATE_MISSING

    if '%' in value:
        try:
            return float(value.replace('%', '').strip()) / 100
        except:
            return AMERICA_RATE_MISSING

    try:
        return float(value)
    except:
        return AMERICA_RATE_MISSING


def map_columns(df):
    """字段映射"""
    df = df.rename(columns=COLUMN_MAPPING)
    return df


def calculate_review_rate(total_sales, comment_count):
    """
    计算留评率（百分比形式）

    业务逻辑：
    - 留评率 = (评论数 / 总销量) × 100
    - 正常范围：0% - 100%
    - 如果评论数 > 总销量，说明数据异常，返回 None

    Args:
        total_sales: 总销量
        comment_count: 评论数

    Returns:
        float: 留评率（百分比，0-100）
        None: 数据异常或总销量为0
    """
    # 总销量为0或负数，无法计算
    if total_sales <= 0:
        return None

    # 评论数为负数，数据异常
    if comment_count < 0:
        return None

    # 异常检测：评论数不可能大于总销量
    if comment_count > total_sales:
        return None  # 标记为异常数据

    # 计算留评率（百分比形式，保留2位小数）
    review_rate = round(comment_count / total_sales * 100, 2)

    # 二次检查：确保不超过100%
    if review_rate > 100:
        return None

    return review_rate


def load_csv(file_path):
    """读取 CSV 或 Excel 文件"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        # 读取 Excel 时指定商品ID列为字符串类型，避免变成浮点数
        df = pd.read_excel(file_path, dtype={'商品ID': str})

    # 确保 product_id 是字符串类型（避免科学计数法和精度问题）
    if 'product_id' in df.columns:
        df['product_id'] = df['product_id'].astype(str)

    # 确保 collect_date 是日期类型
    if 'collect_date' in df.columns:
        df['collect_date'] = pd.to_datetime(df['collect_date']).dt.date

    return df
