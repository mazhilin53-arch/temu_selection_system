# Code 工作区

这是我的代码工作区，用于存放多个独立项目。

## 目录结构

```
code/
├── .claude/                    # Claude AI 配置
├── .gitignore                  # Git 忽略规则（全局）
├── .vscode/                    # VS Code 配置（全局）
│
├── temu_selection_system/      # 项目1：Temu 选品系统
│   ├── backend/                #   后端 API (FastAPI)
│   ├── frontend/               #   前端界面 (Vue 3)
│   ├── data_process/           #   数据处理模块
│   ├── README.md               #   项目说明
│   ├── start.bat               #   启动脚本
│   └── product_data_postgres_20260310_114239.sql  #   数据备份
│
└── [其他项目...]               # 未来可以添加更多项目
```

## 项目列表

### 1. Temu 选品系统 (temu_selection_system)
- **技术栈**: FastAPI + Vue 3 + PostgreSQL
- **用途**: Temu 商品数据筛选与分析系统
- **启动方式**: `cd temu_selection_system && start.bat`

## 添加新项目

在工作区创建新项目：
```bash
mkdir your_new_project
cd your_new_project
# 初始化你的项目...
```

## 注意事项

- 每个项目都是独立的，包含自己的依赖和配置
- 全局配置文件 (.gitignore, .vscode/) 适用于所有项目
- 建议每个项目都有独立的 README.md
