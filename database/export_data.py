#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据导出工具
用于将当前数据库中的数据导出为 SQL 文件，方便团队成员导入

使用方法：
    python export_data.py

输出文件：
    - data_dump.sql（包含所有数据）
"""

import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../data_process'))

import psycopg2
from config import DB_CONFIG


def export_data(output_file='data_dump.sql'):
    """
    导出数据库数据为 SQL 文件

    Args:
        output_file: 输出文件路径
    """
    print(f"[INFO] Starting data export to {output_file}...")

    # 获取数据库连接
    try:
        # 直接创建连接（不使用连接池）
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 打开输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write(f"""-- ============================================================================
-- Temu 选品系统 - 数据导出文件
-- 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- 说明：此文件包含数据库的所有数据，使用 psql 导入即可
-- 导入命令：psql -U postgres -d temu_products -f data_dump.sql
-- ============================================================================

-- 禁用触发器（加速导入）
SET session_replication_role = replica;

-- 清空现有数据（如果存在）
TRUNCATE TABLE raw_products CASCADE;
TRUNCATE TABLE product_history CASCADE;
TRUNCATE TABLE product_main CASCADE;

""")

            # 1. 导出 product_main 表
            print("[INFO] Exporting product_main table...")
            cur.execute("SELECT * FROM product_main")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            if rows:
                f.write(f"-- 导入 product_main 表（{len(rows)} 条记录）\n")
                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append('NULL')
                        elif isinstance(value, str):
                            # 转义单引号
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            values.append(f"'{value}'")

                    f.write(f"INSERT INTO product_main ({', '.join(columns)}) VALUES ({', '.join(values)});\n")

                f.write("\n")
                print(f"[OK] product_main table exported, {len(rows)} records")
            else:
                f.write("-- product_main 表无数据\n\n")
                print("[WARNING] product_main table has no data")

            # 2. 导出 product_history 表
            print("[INFO] Exporting product_history table...")
            cur.execute("SELECT * FROM product_history")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            if rows:
                f.write(f"-- 导入 product_history 表（{len(rows)} 条记录）\n")
                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append('NULL')
                        elif isinstance(value, str):
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            values.append(f"'{value}'")

                    f.write(f"INSERT INTO product_history ({', '.join(columns)}) VALUES ({', '.join(values)});\n")

                f.write("\n")
                print(f"[OK] product_history table exported, {len(rows)} records")
            else:
                f.write("-- product_history 表无数据\n\n")
                print("[WARNING] product_history table has no data")

            # 3. 导出 raw_products 表
            print("[INFO] Exporting raw_products table...")
            cur.execute("SELECT * FROM raw_products")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            if rows:
                f.write(f"-- 导入 raw_products 表（{len(rows)} 条记录）\n")
                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append('NULL')
                        elif isinstance(value, str):
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            values.append(f"'{value}'")

                    f.write(f"INSERT INTO raw_products ({', '.join(columns)}) VALUES ({', '.join(values)});\n")

                f.write("\n")
                print(f"[OK] raw_products table exported, {len(rows)} records")
            else:
                f.write("-- raw_products 表无数据\n\n")
                print("[WARNING] raw_products table has no data")

            # 4. 重置序列
            f.write("""-- 重置自增序列
SELECT setval('product_history_id_seq', (SELECT COALESCE(MAX(id), 0) FROM product_history), true);
SELECT setval('raw_products_id_seq', (SELECT COALESCE(MAX(id), 0) FROM raw_products), true);

-- 恢复触发器
SET session_replication_role = DEFAULT;

-- ============================================================================
-- 数据导入完成
-- ============================================================================

-- 验证数据
SELECT '数据导入完成！' as status;
SELECT '商品总数：' || COUNT(*) as info FROM product_main;
SELECT '历史记录总数：' || COUNT(*) as info FROM product_history;
SELECT '原始记录总数：' || COUNT(*) as info FROM raw_products;
""")

        cur.close()
        conn.close()

        print(f"\n[SUCCESS] Data export completed!")
        print(f"[FILE] Output: {output_file}")
        print(f"[SIZE] File size: {os.path.getsize(output_file) / 1024:.2f} KB")
        print(f"\n[INFO] Team members usage:")
        print(f"   1. Execute schema.sql to create table structure")
        print(f"   2. Execute this file to import data: psql -U postgres -d temu_products -f {output_file}")

    except Exception as e:
        print(f"[ERROR] Export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 70)
    print(" " * 20 + "Temu Data Export Tool")
    print("=" * 70)
    print()

    # 检查数据库配置
    print("[CONFIG] Database connection info:")
    print(f"   Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print()

    # 使用 Python 导出（兼容性最好）
    export_data('data_dump.sql')

    print()
    print("=" * 70)
