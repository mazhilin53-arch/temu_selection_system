#!/usr/bin/env python
# -*- coding: utf-8 -*-
# check_schema.py - 数据库表结构检查工具
import sys
sys.path.insert(0, 'data_process')
from config import DB_CONFIG
import psycopg2

print("=" * 70)
print("Database Schema Check")
print("=" * 70)
print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
print(f"Database: {DB_CONFIG['database']}")
print()

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Get all tables
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    ORDER BY table_name
""")
tables = [row[0] for row in cur.fetchall()]

print(f"Total {len(tables)} tables:")
for table in tables:
    print(f"  - {table}")

print()
print("=" * 70)
print("Table Structure:")
print("=" * 70)

for table in tables:
    print(f"\n[Table: {table}]")
    print("-" * 70)

    cur.execute("""
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table,))

    columns = cur.fetchall()
    for col in columns:
        col_name, data_type, max_length, is_nullable, default_val = col
        type_info = data_type
        if max_length:
            type_info += f"({max_length})"
        nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
        default = f" DEFAULT {default_val}" if default_val else ""
        print(f"  {col_name:<30} {type_info:<20} {nullable:<10}{default}")

cur.close()
conn.close()
print("\nCheck completed!")
