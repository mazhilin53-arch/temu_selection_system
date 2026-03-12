#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
元数据路由
"""

from typing import List
from fastapi import APIRouter, HTTPException
from database import db_pool
from crud import MetadataCRUD
from models import MetadataResponse

router = APIRouter(prefix="/api/metadata", tags=["元数据"])


@router.get("/category-tree", response_model=List[dict])
async def get_category_tree():
    """
    获取级联类目树

    返回按榜单分组的类目树，用于前端级联选择器

    示例响应：
    [
        {
            "ranking_list": "畅销榜",
            "tree": [
                {
                    "name": "家居厨房",
                    "level": 1,
                    "children": [
                        {"name": "厨房用品", "level": 2},
                        {"name": "烹饪工具", "level": 2}
                    ]
                }
            ]
        },
        {
            "ranking_list": "新品榜",
            "tree": [...]"
        }
    ]
    """
    with db_pool.get_connection() as conn:
        try:
            trees = MetadataCRUD.get_category_trees(conn)
            return trees
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询类目树失败: {str(e)}")


@router.get("/overview", response_model=MetadataResponse)
async def get_metadata_overview():
    """
    获取元数据汇总（包括所有级联筛选的选项）

    前端初始化时调用此接口，一次性获取所有元数据
    """
    with db_pool.get_connection() as conn:
        try:
            ranking_lists = MetadataCRUD.get_ranking_lists(conn)
            shop_types = MetadataCRUD.get_shop_types(conn)
            category_trees = MetadataCRUD.get_category_trees(conn)

            # 获取统计信息
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM product_main")
            total_products = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM product_main WHERE latest_date >= CURRENT_DATE - INTERVAL '30 days'")
            active_products = cur.fetchone()[0]
            cur.close()

            return MetadataResponse(
                ranking_lists=ranking_lists,
                category_trees=category_trees,
                shop_types=shop_types,
                total_products=total_products,
                active_products_count=active_products
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询元数据失败: {str(e)}")
