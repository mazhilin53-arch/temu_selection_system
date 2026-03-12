#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库 CRUD 操作
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class ProductCRUD:
    """商品数据 CRUD 操作"""

    @staticmethod
    def build_where_clause(filters: dict) -> Tuple[str, List[Any]]:
        """
        动态构建 WHERE 子句

        Args:
            filters: 筛选条件字典

        Returns:
            (where_sql, params): WHERE子句和参数列表
        """
        conditions = []
        params = []

        # 1. 活跃周期筛选
        if filters.get('active_days'):
            days = filters['active_days']
            cutoff_date = date.today() - timedelta(days=days)
            conditions.append(f"latest_date >= %s")
            params.append(cutoff_date)

        # 2. 级联筛选：榜单、一级类目、二级类目
        if filters.get('ranking_list'):
            conditions.append("ranking_list = %s")
            params.append(filters['ranking_list'])

        if filters.get('category_level1'):
            conditions.append("category_level1 = %s")
            params.append(filters['category_level1'])

        if filters.get('category_level2'):
            conditions.append("category_level2 = %s")
            params.append(filters['category_level2'])

        # 3. 枚举筛选
        if filters.get('shop_type'):
            conditions.append("shop_type = %s")
            params.append(filters['shop_type'])

        if filters.get('is_investigated') is not None:
            conditions.append("is_investigated = %s")
            params.append(int(filters['is_investigated']))

        # 4. 范围筛选：总销量
        if filters.get('total_sales_min') is not None:
            conditions.append("total_sales >= %s")
            params.append(filters['total_sales_min'])

        if filters.get('total_sales_max') is not None:
            conditions.append("total_sales <= %s")
            params.append(filters['total_sales_max'])

        # 5. 范围筛选：日销量
        if filters.get('daily_sales_min') is not None:
            conditions.append("daily_sales >= %s")
            params.append(filters['daily_sales_min'])

        if filters.get('daily_sales_max') is not None:
            conditions.append("daily_sales <= %s")
            params.append(filters['daily_sales_max'])

        # 6. 范围筛选：7天平均日销量
        if filters.get('avg_daily_sales_7d_min') is not None:
            conditions.append("avg_daily_sales_7d >= %s")
            params.append(filters['avg_daily_sales_7d_min'])

        if filters.get('avg_daily_sales_7d_max') is not None:
            conditions.append("avg_daily_sales_7d <= %s")
            params.append(filters['avg_daily_sales_7d_max'])

        # 7. 范围筛选：评论数
        if filters.get('comment_count_min') is not None:
            conditions.append("comment_count >= %s")
            params.append(filters['comment_count_min'])

        if filters.get('comment_count_max') is not None:
            conditions.append("comment_count <= %s")
            params.append(filters['comment_count_max'])

        # 8. 范围筛选：留评率
        if filters.get('review_rate_min') is not None:
            conditions.append("review_rate >= %s")
            params.append(filters['review_rate_min'])

        if filters.get('review_rate_max') is not None:
            conditions.append("review_rate <= %s")
            params.append(filters['review_rate_max'])

        # 9. 范围筛选：价格
        if filters.get('price_min') is not None:
            conditions.append("price >= %s")
            params.append(filters['price_min'])

        if filters.get('price_max') is not None:
            conditions.append("price <= %s")
            params.append(filters['price_max'])

        # 10. 范围筛选：监控次数
        if filters.get('monitor_count_min') is not None:
            conditions.append("monitor_count >= %s")
            params.append(filters['monitor_count_min'])

        if filters.get('monitor_count_max') is not None:
            conditions.append("monitor_count <= %s")
            params.append(filters['monitor_count_max'])

        # 11. 范围筛选：排名
        if filters.get('level2_ranking_min') is not None:
            conditions.append("level2_ranking >= %s")
            params.append(filters['level2_ranking_min'])

        if filters.get('level2_ranking_max') is not None:
            conditions.append("level2_ranking <= %s")
            params.append(filters['level2_ranking_max'])

        # 组装 WHERE 子句
        where_sql = ""
        if conditions:
            where_sql = " WHERE " + " AND ".join(conditions)

        return where_sql, params

    @staticmethod
    def build_order_by(sort_by: str, sort_order: str) -> str:
        """
        构建 ORDER BY 子句

        Args:
            sort_by: 排序字段
            sort_order: 排序方向（asc/desc）

        Returns:
            ORDER BY 子句
        """
        # 允许的排序字段
        allowed_fields = {
            'total_sales', 'daily_sales', 'price', 'comment_count',
            'review_rate', 'monitor_count', 'level2_ranking',
            'avg_daily_sales_7d'
        }

        if sort_by not in allowed_fields:
            sort_by = 'total_sales'  # 默认按总销量排序

        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'  # 默认降序

        return f"ORDER BY {sort_by} {sort_order}"

    @staticmethod
    def get_products(conn, filters: dict, offset: int = 0, limit: int = 20) -> Tuple[int, List[dict]]:
        """
        查询商品列表

        Args:
            conn: 数据库连接
            filters: 筛选条件
            offset: 偏移量（分页用）
            limit: 限制数量

        Returns:
            (total_count, items): 总记录数和商品列表
        """
        # 构建查询
        base_query = "SELECT COUNT(*) FROM product_main"
        data_query = """
            SELECT
                product_id, link, product_title, image_url,
                category_level1, category_level2, ranking_list, shop_type,
                latest_date, price, daily_sales, total_sales, comment_count,
                level1_ranking, level2_ranking, review_rate,
                avg_daily_sales_7d, monitor_count, is_investigated
            FROM product_main
        """

        # 构建 WHERE 子句
        where_sql, params = ProductCRUD.build_where_clause(filters)
        data_query += where_sql

        # 获取总数
        count_query = base_query + where_sql
        cur = conn.cursor()
        cur.execute(count_query, params)
        total_count = cur.fetchone()[0]

        # 添加排序和分页
        order_sql = ProductCRUD.build_order_by(
            filters.get('sort_by', 'total_sales'),
            filters.get('sort_order', 'desc')
        )
        data_query += f" {order_sql}"
        data_query += f" LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        # 执行查询
        cur.execute(data_query, params)
        columns = [
            'product_id', 'link', 'product_title', 'image_url',
            'category_level1', 'category_level2', 'ranking_list', 'shop_type',
            'latest_date', 'price', 'daily_sales', 'total_sales', 'comment_count',
            'level1_ranking', 'level2_ranking', 'review_rate',
            'avg_daily_sales_7d', 'monitor_count', 'is_investigated'
        ]

        items = []
        for row in cur.fetchall():
            item = dict(zip(columns, row))
            # 转换日期为字符串
            if item['latest_date']:
                item['latest_date'] = item['latest_date'].isoformat()
            items.append(item)

        cur.close()
        return total_count, items

    @staticmethod
    def get_product_by_id(conn, product_id: str) -> Optional[dict]:
        """根据ID获取商品详情"""
        query = """
            SELECT
                product_id, link, product_title, image_url,
                category_level1, category_level2, ranking_list, shop_type,
                latest_date, price, daily_sales, total_sales, comment_count,
                level1_ranking, level2_ranking, review_rate,
                avg_daily_sales_7d, monitor_count, is_investigated
            FROM product_main
            WHERE product_id = %s
        """

        cur = conn.cursor()
        cur.execute(query, (product_id,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return None

        columns = [
            'product_id', 'link', 'product_title', 'image_url',
            'category_level1', 'category_level2', 'ranking_list', 'shop_type',
            'latest_date', 'price', 'daily_sales', 'total_sales', 'comment_count',
            'level1_ranking', 'level2_ranking', 'review_rate',
            'avg_daily_sales_7d', 'monitor_count', 'is_investigated'
        ]

        item = dict(zip(columns, row))
        if item['latest_date']:
            item['latest_date'] = item['latest_date'].isoformat()

        return item

    @staticmethod
    def get_product_history(
        conn,
        product_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Optional[dict]:
        """
        获取商品历史趋势数据

        Args:
            conn: 数据库连接
            product_id: 商品ID
            start_date: 开始日期（None表示所有历史）
            end_date: 结束日期（None表示所有历史）

        Returns:
            商品历史数据和5个趋势图数据
        """
        # 获取商品基本信息
        product_query = """
            SELECT product_id, product_title
            FROM product_main
            WHERE product_id = %s
        """

        # 构建历史查询
        history_query = """
            SELECT
                collect_date,
                price,
                daily_sales,
                total_sales,
                comment_count,
                level2_ranking
            FROM product_history
            WHERE product_id = %s
        """

        params = [product_id]

        # 添加日期范围筛选
        if start_date:
            history_query += " AND collect_date >= %s"
            params.append(start_date)

        if end_date:
            history_query += " AND collect_date <= %s"
            params.append(end_date)

        history_query += " ORDER BY collect_date ASC"

        cur = conn.cursor()

        # 查询商品信息
        cur.execute(product_query, (product_id,))
        product_row = cur.fetchone()

        if not product_row:
            cur.close()
            return None

        # 查询历史数据
        cur.execute(history_query, params)
        history_rows = cur.fetchall()
        cur.close()

        if not history_rows:
            return {
                'product_id': product_id,
                'product_title': product_row[1],
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'items': [],
                'total_sales_trend': [],
                'daily_sales_trend': [],
                'comment_count_trend': [],
                'price_trend': [],
                'ranking_trend': []
            }

        # 解析历史数据
        items = []
        dates = []
        total_sales_data = []
        daily_sales_data = []
        comment_count_data = []
        price_data = []
        ranking_data = []

        for row in history_rows:
            dates.append(row[0].isoformat())
            price_data.append({"date": row[0].isoformat(), "value": float(row[1])})
            daily_sales_data.append({"date": row[0].isoformat(), "value": int(row[2])})
            total_sales_data.append({"date": row[0].isoformat(), "value": int(row[3])})
            comment_count_data.append({"date": row[0].isoformat(), "value": int(row[4])})
            ranking_data.append({"date": row[0].isoformat(), "value": int(row[5])})

            items.append({
                'collect_date': row[0].isoformat(),
                'price': float(row[1]),
                'daily_sales': int(row[2]),
                'total_sales': int(row[3]),
                'comment_count': int(row[4]),
                'level2_ranking': int(row[5])
            })

        return {
            'product_id': product_id,
            'product_title': product_row[1],
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'items': items,
            'total_sales_trend': total_sales_data,
            'daily_sales_trend': daily_sales_data,
            'comment_count_trend': comment_count_data,
            'price_trend': price_data,
            'ranking_trend': ranking_data
        }


class MetadataCRUD:
    """元数据 CRUD 操作"""

    @staticmethod
    def get_category_trees(conn) -> List[dict]:
        """
        获取级联类目树（按榜单分组）

        Returns:
            类目树列表
        """
        query = """
        SELECT DISTINCT
            ranking_list,
            category_level1,
            category_level2
        FROM product_main
        WHERE ranking_list IS NOT NULL
        ORDER BY ranking_list, category_level1, category_level2
        """

        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()

        # 构建树形结构
        ranking_dict = {}

        for ranking, cat1, cat2 in rows:
            if ranking not in ranking_dict:
                ranking_dict[ranking] = {}

            if cat1 not in ranking_dict[ranking]:
                ranking_dict[ranking][cat1] = set()

            ranking_dict[ranking][cat1].add(cat2)

        # 转换为前端需要的格式
        trees = []
        for ranking, categories in ranking_dict.items():
            tree_nodes = []
            for cat1, cat2_set in categories.items():
                children = [
                    {"name": cat2, "level": 2}
                    for cat2 in sorted(cat2_set)
                ]
                tree_nodes.append({
                    "name": cat1,
                    "level": 1,
                    "children": children
                })

            trees.append({
                "ranking_list": ranking,
                "tree": tree_nodes
            })

        return trees

    @staticmethod
    def get_shop_types(conn) -> List[str]:
        """获取所有店铺类型"""
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT shop_type FROM product_main WHERE shop_type IS NOT NULL ORDER BY shop_type")
        shop_types = [row[0] for row in cur.fetchall()]
        cur.close()
        return shop_types

    @staticmethod
    def get_ranking_lists(conn) -> List[str]:
        """获取所有榜单"""
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT ranking_list FROM product_main WHERE ranking_list IS NOT NULL ORDER BY ranking_list")
        ranking_lists = [row[0] for row in cur.fetchall()]
        cur.close()
        return ranking_lists

    @staticmethod
    def search_products(
        conn,
        keyword: str,
        limit: int = 10
    ) -> List[dict]:
        """
        搜索商品（根据ID或标题）

        Args:
            conn: 数据库连接
            keyword: 搜索关键词
            limit: 返回数量限制

        Returns:
            匹配的商品列表
        """
        query = """
            SELECT
                product_id,
                product_title,
                category_level1,
                total_sales,
                latest_date
            FROM product_main
            WHERE product_id LIKE %s
               OR product_title LIKE %s
            ORDER BY total_sales DESC
            LIMIT %s
        """

        cur = conn.cursor()
        cur.execute(query, (f"%{keyword}%", f"%{keyword}%", limit))
        rows = cur.fetchall()
        cur.close()

        return [
            {
                'product_id': row[0],
                'product_title': row[1],
                'category_level1': row[2],
                'total_sales': row[3],
                'latest_date': row[4].isoformat()
            }
            for row in rows
        ]
