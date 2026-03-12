#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI 后端主入口
"""
import sys
from pathlib import Path

# 添加backend和data_process目录到系统路径
# 注意：backend必须在前，优先从backend导入
backend_dir = Path(__file__).parent
data_process_dir = backend_dir.parent / "data_process"

# 清理可能存在的冲突路径
sys.path = [p for p in sys.path if 'backend' not in p and 'data_process' not in p]

# 添加路径（backend在前，确保优先）
sys.path.insert(0, str(backend_dir))
sys.path.append(str(data_process_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routers import products, metadata
from database import db_pool

# 创建 FastAPI 应用
app = FastAPI(
    title="Temu 选品系统 API",
    description="基于 PostgreSQL 双表架构的商品选品后端系统",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """应用启动时初始化数据库连接池"""
    db_pool.init_pool()
    print("[OK] Database pool initialized")


@app.on_event("shutdown")
async def shutdown():
    """应用关闭时释放数据库连接池"""
    db_pool.close()
    print("[OK] Database pool closed")


@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "Temu 选品系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}


# 注册路由
app.include_router(products.router)
app.include_router(metadata.router)


if __name__ == "__main__":
    # 启动服务器
    print("=" * 80)
    print("Temu 选品系统 API 服务启动")
    print("=" * 80)
    print("API 文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    print("=" * 80)

    uvicorn.run(
        app,
        host="0.0.0.0",  # 允许局域网访问
        port=8000,
        reload=False,  # 直接运行时禁用 reload
        log_level="info"
    )
