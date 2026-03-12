# Temu 选品系统 - 前端

美观的 Vue 3 前端应用，基于 Element Plus 和 ECharts 构建。

## 🎨 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3 UI 组件库
- **ECharts** - 强大的数据可视化库
- **Vue Router** - 官方路由管理器
- **Axios** - HTTP 客户端

## 🚀 快速开始

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

访问：http://localhost:5173

### 构建生产版本
```bash
npm run build
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口
│   │   └── index.js
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── views/            # 页面组件
│   │   ├── ProductList.vue    # 商品列表页
│   │   └── ProductDetail.vue  # 商品详情页
│   ├── App.vue           # 根组件
│   ├── main.js           # 入口文件
│   └── style.css         # 全局样式
├── index.html
├── package.json
└── vite.config.js
```

## ✨ 功能特性

### 商品列表页
- ✅ 18种筛选条件（活跃周期、级联筛选、范围筛选、枚举筛选）
- ✅ 美观的筛选面板布局
- ✅ 数据表格展示（可点击行查看详情）
- ✅ 分页功能（支持10/20/50/100条每页）
- ✅ 多字段排序

### 商品详情页
- ✅ 顶部搜索框（防抖自动完成）
- ✅ 全局日期控制器（控制所有图表）
- ✅ 商品基本信息展示
- ✅ 5个ECharts趋势图：
  - 总销量趋势
  - 日销量趋势
  - 评论数趋势
  - 价格趋势
  - 排名趋势
- ✅ 图表支持 dataZoom 缩放
- ✅ 响应式布局

## 🎯 API 对接

前端已完全对接后端 API：

- `GET /api/products/list` - 商品列表
- `GET /api/products/{id}` - 商品详情
- `GET /api/products/{id}/history` - 历史趋势
- `GET /api/products/search` - 搜索
- `GET /api/metadata/category-tree` - 类目树

后端服务地址：`http://127.0.0.1:8000`

## 🎨 界面预览

### 商品列表页
- 精美的筛选面板
- 清晰的数据表格
- 直观的分页器

### 商品详情页
- 便捷的搜索功能
- 完整的商品信息
- 交互式趋势图表

## 📝 开发说明

### 添加新页面
1. 在 `src/views/` 创建组件
2. 在 `src/router/index.js` 添加路由

### 添加新 API
在 `src/api/index.js` 添加接口方法

### 自定义样式
- 全局样式：`src/style.css`
- 组件样式：Vue 文件 `<style scoped>`

## 🌟 特色

- 🎨 **美观设计** - 基于 Element Plus 的现代化 UI
- 📊 **数据可视化** - ECharts 交互式图表
- 🔍 **智能搜索** - 防抖自动完成
- 📱 **响应式布局** - 适配不同屏幕尺寸
- ⚡ **快速开发** - Vite 热更新

---

**开发时间**: 2026-03-11
**版本**: 1.0.0
