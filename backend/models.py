#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pydantic 模型定义
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date, datetime


# =============================================================================
# 商品筛选模型
# =============================================================================

class ProductFilter(BaseModel):
    """商品筛选条件"""

    # 活跃周期（天数）
    active_days: Optional[int] = Field(
        30,
        description="最近N天有数据的商品（默认30天）"
    )

    # 级联筛选
    ranking_list: Optional[str] = Field(
        None,
        description="榜单（畅销榜/新品榜）"
    )
    category_level1: Optional[str] = Field(
        None,
        description="一级类目"
    )
    category_level2: Optional[str] = Field(
        None,
        description="二级类目"
    )

    # 枚举筛选
    shop_type: Optional[str] = Field(
        None,
        description="店铺类型（全托管/半托管）"
    )
    is_investigated: Optional[bool] = Field(
        None,
        description="是否已调研"
    )

    # 范围筛选
    total_sales_min: Optional[int] = Field(
        None,
        description="总销量最小值"
    )
    total_sales_max: Optional[int] = Field(
        None,
        description="总销量最大值"
    )

    daily_sales_min: Optional[int] = Field(
        None,
        description="日销量最小值"
    )
    daily_sales_max: Optional[int] = Field(
        None,
        description="日销量最大值"
    )

    avg_daily_sales_7d_min: Optional[int] = Field(
        None,
        description="7天平均日销量最小值"
    )
    avg_daily_sales_7d_max: Optional[int] = Field(
        None,
        description="7天平均日销量最大值"
    )

    comment_count_min: Optional[int] = Field(
        None,
        description="评论数最小值"
    )
    comment_count_max: Optional[int] = Field(
        None,
        description="评论数最大值"
    )

    review_rate_min: Optional[float] = Field(
        None,
        description="留评率最小值（百分比，如 5.0 表示 5%）"
    )
    review_rate_max: Optional[float] = Field(
        None,
        description="留评率最大值（百分比，如 10.0 表示 10%）"
    )

    price_min: Optional[float] = Field(
        None,
        description="价格最小值"
    )
    price_max: Optional[float] = Field(
        None,
        description="价格最大值"
    )

    monitor_count_min: Optional[int] = Field(
        None,
        description="监控次数最小值"
    )
    monitor_count_max: Optional[int] = Field(
        None,
        description="监控次数最大值"
    )

    level2_ranking_min: Optional[int] = Field(
        None,
        description="二级类目排名最小值"
    )
    level2_ranking_max: Optional[int] = Field(
        None,
        description="二级类目排名最大值"
    )

    # 排序
    sort_by: Optional[str] = Field(
        "total_sales",
        description="排序字段（total_sales/daily_sales/price/comment_count/review_rate/monitor_count/level2_ranking）"
    )
    sort_order: Optional[str] = Field(
        "desc",
        description="排序方向（asc/desc）"
    )

    # 分页
    page: Optional[int] = Field(
        1,
        ge=1,
        description="页码（从1开始）"
    )
    page_size: Optional[int] = Field(
        20,
        ge=1,
        le=100,
        description="每页数量（最大100）"
    )


# =============================================================================
# 商品响应模型
# =============================================================================

class ProductListItem(BaseModel):
    """商品列表项"""
    product_id: str
    link: str
    product_title: str
    image_url: Optional[str]
    category_level1: str
    category_level2: str
    ranking_list: str
    shop_type: str
    latest_date: date
    price: float
    daily_sales: int
    total_sales: int
    comment_count: int
    level1_ranking: int
    level2_ranking: int
    review_rate: Optional[float]
    avg_daily_sales_7d: int
    monitor_count: int
    is_investigated: int

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """商品列表响应"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: List[ProductListItem] = Field(..., description="商品列表")


# =============================================================================
# 商品详情模型
# =============================================================================

class ProductDetail(BaseModel):
    """商品详情"""
    product_id: str
    link: str
    product_title: str
    image_url: Optional[str]
    category_level1: str
    category_level2: str
    ranking_list: str
    shop_type: str
    latest_date: date
    price: float
    daily_sales: int
    total_sales: int
    comment_count: int
    level1_ranking: int
    level2_ranking: int
    review_rate: Optional[float]
    avg_daily_sales_7d: int
    monitor_count: int
    is_investigated: int

    class Config:
        from_attributes = True


# =============================================================================
# 商品历史模型
# =============================================================================

class ProductHistoryItem(BaseModel):
    """商品历史记录"""
    collect_date: date
    price: float
    daily_sales: int
    total_sales: int
    comment_count: int
    level2_ranking: int

    class Config:
        from_attributes = True


class ProductHistoryResponse(BaseModel):
    """商品历史趋势响应"""
    product_id: str
    product_title: str
    start_date: Optional[date]
    end_date: Optional[date]
    items: List[ProductHistoryItem]

    # 5个趋势图的数据
    total_sales_trend: List[dict] = Field(..., description="总销量趋势")
    daily_sales_trend: List[dict] = Field(..., description="日销量趋势")
    comment_count_trend: List[dict] = Field(..., description="评论数趋势")
    price_trend: List[dict] = Field(..., description="价格趋势")
    ranking_trend: List[dict] = Field(..., description="排名趋势")


# =============================================================================
# 元数据模型
# =============================================================================

class CategoryTreeNode(BaseModel):
    """类目树节点"""
    name: str
    level: int  # 1=一级类目, 2=二级类目
    children: List['CategoryTreeNode'] = []


class CategoryTreeResponse(BaseModel):
    """级联类目树响应"""
    ranking_list: str
    tree: List[CategoryTreeNode]


class MetadataResponse(BaseModel):
    """元数据响应（汇总）"""
    # 榜单列表
    ranking_lists: List[str]

    # 每个榜单对应的类目树
    category_trees: List[CategoryTreeResponse]

    # 店铺类型
    shop_types: List[str]

    # 统计信息
    total_products: int
    active_products_count: int


# =============================================================================
# 搜索模型
# =============================================================================

class SearchSuggestion(BaseModel):
    """搜索建议项"""
    product_id: str
    product_title: str
    category_level1: str
    total_sales: int
    latest_date: date


# =============================================================================
# 通用响应模型
# =============================================================================

class ApiResponse(BaseModel):
    """通用 API 响应"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None
