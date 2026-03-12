import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://192.168.2.22:8000',  // 使用局域网IP
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API 接口
export const api = {
  // 获取商品列表
  getProductList(params) {
    return request.get('/api/products/list', { params })
  },

  // 获取商品详情
  getProductDetail(productId) {
    return request.get(`/api/products/${productId}`)
  },

  // 获取商品历史趋势
  getProductHistory(productId, params = {}) {
    return request.get(`/api/products/${productId}/history`, { params })
  },

  // 搜索商品
  searchProducts(keyword, limit = 10) {
    return request.get('/api/products/search', {
      params: { keyword, limit }
    })
  },

  // 获取级联类目树
  getCategoryTree() {
    return request.get('/api/metadata/category-tree')
  },

  // 获取元数据汇总
  getMetadataOverview() {
    return request.get('/api/metadata/overview')
  },

  // 批量标记商品为已调研/未调研
  markProductsInvestigated(productIds, isInvestigated = true) {
    return request.post('/api/products/mark-investigated', {
      product_ids: productIds,
      is_investigated: isInvestigated
    })
  }
}

export default request
