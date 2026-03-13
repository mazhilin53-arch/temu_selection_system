#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接管理
"""

import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config import DB_CONFIG


class DatabasePool:
    """数据库连接池"""

    def __init__(self):
        self.pool = None

    def init_pool(self):
        """初始化连接池"""
        self.pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,  # 连接池大小
            **DB_CONFIG
        )

    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        if self.pool is None:
            self.init_pool()

        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def close(self):
        """关闭连接池"""
        if self.pool:
            self.pool.closeall()
            self.pool = None


# 全局连接池实例
db_pool = DatabasePool()
