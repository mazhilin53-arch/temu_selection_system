#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接模块
"""

import psycopg2
from config import DB_CONFIG


class DatabaseConnection:
    """数据库连接管理器"""

    def __init__(self):
        self.conn = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False

    def get_connection(self):
        """获取连接对象"""
        if self.conn is None:
            if not self.connect():
                return None
        return self.conn

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
