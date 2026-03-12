#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
商品路由
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from database import db_pool
from crud import ProductCRUD, MetadataCRUD
from models import (
    ProductListResponse,
    ProductListItem,
    ProductDetail,
    ProductHistoryResponse,
    SearchSuggestion
)

router = APIRouter(prefix="/api/products", tags=["商品"])


@router.get("/list", response_model=ProductListResponse)
async def get_products(
    # 活跃周期筛选
    active_days: Optional[int] = Query(
        30,
        description="最近N天有数据的商品"
    ),
    # 级联筛选
    ranking_list: Optional[str] = Query(None, description="榜单"),
    category_level1: Optional[str] = Query(None, description="一级类目"),
    category_level2: Optional[str] = Query(None, description="二级类目"),
    # 枚举筛选
    shop_type: Optional[str] = Query(None, description="店铺类型"),
    is_investigated: Optional[bool] = Query(None, description="是否已调研"),
    # 范围筛选：总销量
    total_sales_min: Optional[int] = Query(None, description="总销量最小值"),
    total_sales_max: Optional[int] = Query(None, description="总销量最大值"),
    # 范围筛选：日销量
    daily_sales_min: Optional[int] = Query(None, description="日销量最小值"),
    daily_sales_max: Optional[int] = Query(None, description="日销量最大值"),
    # 范围筛选：7天平均日销量
    avg_daily_sales_7d_min: Optional[int] = Query(None, description="7天平均日销量最小值"),
    avg_daily_sales_7d_max: Optional[int] = Query(None, description="7天平均日销量最大值"),
    # 范围筛选：评论数
    comment_count_min: Optional[int] = Query(None, description="评论数最小值"),
    comment_count_max: Optional[int] = Query(None, description="评论数最大值"),
    # 范围筛选：留评率
    review_rate_min: Optional[float] = Query(None, description="留评率最小值（百分比）"),
    review_rate_max: Optional[float] = Query(None, description="留评率最大值（百分比）"),
    # 范围筛选：价格
    price_min: Optional[float] = Query(None, description="价格最小值"),
    price_max: Optional[float] = Query(None, description="价格最大值"),
    # 范围筛选：监控次数
    monitor_count_min: Optional[int] = Query(None, description="监控次数最小值"),
    monitor_count_max: Optional[int] = Query(None, description="监控次数最大值"),
    # 范围筛选：排名
    level2_ranking_min: Optional[int] = Query(None, description="二级类目排名最小值"),
    level2_ranking_max: Optional[int] = Query(None, description="二级类目排名最大值"),
    # 排序
    sort_by: Optional[str] = Query("total_sales", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方向"),
    # 分页
    page: Optional[int] = Query(1, ge=1, description="页码"),
    page_size: Optional[int] = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取商品列表（支持18种筛选条件 + 分页 + 排序）

    筛选说明：
    - active_days: 活跃周期（天数），筛选最新数据日期在最近N天的商品
    - ranking_list, category_level1, category_level2: 级联筛选（三级联动）
    - shop_type: 店铺类型（全托管/半托管）
    - is_investigated: 是否已调研
    - 各种 *_min / *_max: 范围筛选参数
    - sort_by: 排序字段（total_sales/daily_sales/price等）
    - sort_order: 排序方向（asc/desc）
    - page: 页码（从1开始）
    - page_size: 每页数量（最大100）
    """
    # 构建筛选条件字典
    filters = {
        'active_days': active_days,
        'ranking_list': ranking_list,
        'category_level1': category_level1,
        'category_level2': category_level2,
        'shop_type': shop_type,
        'is_investigated': is_investigated,
        'total_sales_min': total_sales_min,
        'total_sales_max': total_sales_max,
        'daily_sales_min': daily_sales_min,
        'daily_sales_max': daily_sales_max,
        'avg_daily_sales_7d_min': avg_daily_sales_7d_min,
        'avg_daily_sales_7d_max': avg_daily_sales_7d_max,
        'comment_count_min': comment_count_min,
        'comment_count_max': comment_count_max,
        'review_rate_min': review_rate_min,
        'review_rate_max': review_rate_max,
        'price_min': price_min,
        'price_max': price_max,
        'monitor_count_min': monitor_count_min,
        'monitor_count_max': monitor_count_max,
        'level2_ranking_min': level2_ranking_min,
        'level2_ranking_max': level2_ranking_max,
        'sort_by': sort_by,
        'sort_order': sort_order
    }

    # 计算偏移量
    offset = (page - 1) * page_size

    # 查询数据库
    with db_pool.get_connection() as conn:
        try:
            total, items = ProductCRUD.get_products(conn, filters, offset, page_size)

            return ProductListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=items
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询商品列表失败: {str(e)}")


@router.get("/search", response_model=List[SearchSuggestion])
async def search_products(
    keyword: str = Query(..., min_length=1, description="搜索关键词（商品ID或标题）"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量")
):
    """
    搜索商品（用于详情页的自动完成功能）

    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制

    Returns:
        匹配的商品建议列表

    前端防抖说明：
    - 此接口应配合防抖使用（推荐300ms延迟）
    - 用户输入停止后才发起请求
    - 用户从下拉列表中选择后才跳转到详情页
    """
    with db_pool.get_connection() as conn:
        try:
            results = MetadataCRUD.search_products(conn, keyword, limit)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product_detail(product_id: str):
    """
    获取商品详情

    Args:
        product_id: 商品ID

    Returns:
        商品详情信息
    """
    with db_pool.get_connection() as conn:
        try:
            product = ProductCRUD.get_product_by_id(conn, product_id)

            if not product:
                raise HTTPException(status_code=404, detail=f"商品不存在: {product_id}")

            return product
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询商品详情失败: {str(e)}")


@router.get("/{product_id}/history", response_model=ProductHistoryResponse)
async def get_product_history(
    product_id: str,
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）")
):
    """
    获取商品历史趋势数据（用于5个趋势图）

    Args:
        product_id: 商品ID
        start_date: 开始日期（可选，None表示所有历史）
        end_date: 结束日期（可选，None表示所有历史）

    Returns:
        商品历史数据和5个趋势图数据：
        - total_sales_trend: 总销量趋势
        - daily_sales_trend: 日销量趋势
        - comment_count_trend: 评论数趋势
        - price_trend: 价格趋势
        - ranking_trend: 排名趋势

    前端全局日期控制器说明：
    - 当用户未选择日期范围（start_date和end_date都为None）时，返回所有历史数据
    - 前端应将"全部"选项发送为None或不传这两个参数
    """
    with db_pool.get_connection() as conn:
        try:
            result = ProductCRUD.get_product_history(conn, product_id, start_date, end_date)

            if not result:
                raise HTTPException(status_code=404, detail=f"商品不存在: {product_id}")

            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询商品历史失败: {str(e)}")


# 请求模型
class MarkInvestigatedRequest(BaseModel):
    product_ids: List[str]
    is_investigated: bool = True


@router.post("/mark-investigated")
async def mark_products_investigated(request: MarkInvestigatedRequest):
    """
    批量标记商品为已调研/未调研

    Args:
        request: 包含商品ID列表和标记状态的请求体

    Returns:
        更新结果统计
    """
    with db_pool.get_connection() as conn:
        try:
            cur = conn.cursor()

            # 批量更新
            update_sql = """
            UPDATE product_main
            SET is_investigated = %s
            WHERE product_id = ANY(%s)
            """

            cur.execute(update_sql, (int(request.is_investigated), request.product_ids))
            updated_count = cur.rowcount

            conn.commit()
            cur.close()

            return {
                "success": True,
                "message": f"成功更新 {updated_count} 条商品记录",
                "updated_count": updated_count,
                "product_ids": request.product_ids
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"标记商品失败: {str(e)}")
