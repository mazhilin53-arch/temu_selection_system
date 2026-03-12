<template>
  <div class="product-detail-page">
    <!-- 空白状态 -->
    <div v-if="!currentProductId" class="empty-state">
      <div class="empty-content">
        <el-icon :size="80" class="empty-icon"><Search /></el-icon>
        <h2>商品详情区</h2>
        <p>请选择或搜索商品查看详情</p>
        <el-autocomplete
          v-model="searchKeyword"
          :fetch-suggestions="handleSearch"
          placeholder="搜索商品ID或标题..."
          :debounce="300"
          clearable
          @select="handleSelectProduct"
          style="width: 400px"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #default="{ item }">
            <div class="search-result-item">
              <div class="result-title">{{ item.product_title }}</div>
              <div class="result-meta">
                <span class="result-id">{{ item.product_id }}</span>
                <span>销量: {{ formatNumber(item.total_sales) }}</span>
              </div>
            </div>
          </template>
        </el-autocomplete>
      </div>
    </div>

    <!-- 商品详情 -->
    <div v-else class="detail-content">
      <!-- 顶部导航栏 -->
      <nav class="top-nav">
        <div class="nav-left">
          <el-button @click="clearProduct" circle size="large">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <div class="nav-title">
            <h1>商品详情</h1>
            <code>{{ productInfo.product_id }}</code>
          </div>
        </div>

        <div class="nav-center">
          <el-autocomplete
            v-model="searchKeyword"
            :fetch-suggestions="handleSearch"
            placeholder="搜索商品ID或标题..."
            :debounce="300"
            clearable
            @select="handleSelectProduct"
            style="width: 400px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #default="{ item }">
              <div class="search-result-item">
                <div class="result-title">{{ item.product_title }}</div>
                <div class="result-meta">
                  <span class="result-id">{{ item.product_id }}</span>
                  <span>销量: {{ formatNumber(item.total_sales) }}</span>
                </div>
              </div>
            </template>
          </el-autocomplete>
        </div>

        <div class="nav-right">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
            @change="handleDateChange"
          />
          <el-button type="primary" @click="loadHistoryData" :loading="chartsLoading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </nav>

      <!-- 商品基本信息 -->
      <el-card class="info-card" shadow="hover" v-loading="infoLoading">
        <template #header>
          <div class="card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>商品基本信息</span>
          </div>
        </template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="商品ID" :span="1">
            <el-tag
              class="product-id-tag"
              @click="copyProductId(productInfo.product_id)"
              size="large"
            >
              {{ productInfo.product_id }}
              <el-icon class="copy-icon"><CopyDocument /></el-icon>
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="商品标题" :span="2">
            {{ productInfo.product_title }}
          </el-descriptions-item>
          <el-descriptions-item label="一级类目">
            {{ productInfo.category_level1 }}
          </el-descriptions-item>
          <el-descriptions-item label="二级类目">
            {{ productInfo.category_level2 }}
          </el-descriptions-item>
          <el-descriptions-item label="榜单">
            {{ productInfo.ranking_list }}
          </el-descriptions-item>
          <el-descriptions-item label="店铺类型">
            {{ productInfo.shop_type }}
          </el-descriptions-item>
          <el-descriptions-item label="价格">
            ${{ productInfo.price?.toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item label="日销量">
            {{ formatNumber(productInfo.daily_sales) }}
          </el-descriptions-item>
          <el-descriptions-item label="总销量">
            {{ formatNumber(productInfo.total_sales) }}
          </el-descriptions-item>
          <el-descriptions-item label="评论数">
            {{ formatNumber(productInfo.comment_count) }}
          </el-descriptions-item>
          <el-descriptions-item label="留评率">
            {{ productInfo.review_rate ? productInfo.review_rate + '%' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="7天平均日销">
            {{ formatNumber(productInfo.avg_daily_sales_7d) }}
          </el-descriptions-item>
          <el-descriptions-item label="监控次数">
            {{ productInfo.monitor_count }}
          </el-descriptions-item>
          <el-descriptions-item label="类目排名">
            {{ productInfo.level2_ranking }}
          </el-descriptions-item>
          <el-descriptions-item label="最新日期">
            {{ productInfo.latest_date }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 5个趋势图 -->
      <div class="charts-container">
        <!-- 总销量趋势 -->
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <el-icon><TrendCharts /></el-icon>
              <span>总销量趋势</span>
            </div>
          </template>
          <div ref="totalSalesChartRef" class="chart" v-loading="chartsLoading"></div>
        </el-card>

        <!-- 日销量趋势 -->
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <el-icon><DataLine /></el-icon>
              <span>日销量趋势</span>
            </div>
          </template>
          <div ref="dailySalesChartRef" class="chart" v-loading="chartsLoading"></div>
        </el-card>

        <!-- 评论数趋势 -->
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>评论数趋势</span>
            </div>
          </template>
          <div ref="commentChartRef" class="chart" v-loading="chartsLoading"></div>
        </el-card>

        <!-- 价格趋势 -->
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <el-icon><Money /></el-icon>
              <span>价格趋势</span>
            </div>
          </template>
          <div ref="priceChartRef" class="chart" v-loading="chartsLoading"></div>
        </el-card>

        <!-- 排名趋势 -->
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="chart-header">
              <el-icon><Trophy /></el-icon>
              <span>排名趋势</span>
            </div>
          </template>
          <div ref="rankingChartRef" class="chart" v-loading="chartsLoading"></div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { CopyDocument, Search, InfoFilled, ArrowLeft, Refresh, TrendCharts, DataLine, ChatDotRound, Money, Trophy } from '@element-plus/icons-vue'

const route = useRoute()

// Data
const currentProductId = ref(null)
const productInfo = ref({})
const searchKeyword = ref('')
const dateRange = ref(null)

// Loading states
const infoLoading = ref(false)
const chartsLoading = ref(false)

// Chart refs
const totalSalesChartRef = ref(null)
const dailySalesChartRef = ref(null)
const commentChartRef = ref(null)
const priceChartRef = ref(null)
const rankingChartRef = ref(null)

let charts = []

// Initialize chart
const initChart = (refElement, title, data, color, yAxisType = 'value') => {
  const chart = echarts.init(refElement)
  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}'
    },
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 100
      },
      {
        type: 'inside',
        xAxisIndex: [0],
        start: 0,
        end: 100
      }
    ],
    xAxis: {
      type: 'category',
      data: data.map(item => item.date),
      axisLabel: {
        rotate: 45,
        formatter: (value) => {
          // 格式化日期，只显示月日
          if (value && value.includes('-')) {
            const parts = value.split('-')
            if (parts.length >= 3) {
              return `${parts[1]}-${parts[2]}` // MM-DD
            }
          }
          return value
        }
      }
    },
    yAxis: {
      type: yAxisType
    },
    series: [
      {
        name: title,
        type: 'line',
        data: data.map(item => item.value),
        smooth: true,
        lineStyle: {
          color: color,
          width: 2
        },
        itemStyle: {
          color: color
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + '40' },
            { offset: 1, color: color + '05' }
          ])
        }
      }
    ]
  }
  chart.setOption(option)
  return chart
}

// Load product info
const loadProductInfo = async (productId) => {
  infoLoading.value = true
  try {
    productInfo.value = await api.getProductDetail(productId)
  } catch (error) {
    ElMessage.error('加载商品信息失败：' + (error.response?.data?.detail || error.message))
  } finally {
    infoLoading.value = false
  }
}

// Load history data
const loadHistoryData = async () => {
  if (!currentProductId.value) return

  chartsLoading.value = true
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const data = await api.getProductHistory(currentProductId.value, params)

    await nextTick()

    // Dispose old charts
    charts.forEach(chart => chart.dispose())
    charts = []

    // Create new charts
    charts.push(initChart(totalSalesChartRef.value, '总销量', data.total_sales_trend, '#3B82F6'))
    charts.push(initChart(dailySalesChartRef.value, '日销量', data.daily_sales_trend, '#60A5FA'))
    charts.push(initChart(commentChartRef.value, '评论数', data.comment_count_trend, '#93C5FD'))
    charts.push(initChart(priceChartRef.value, '价格', data.price_trend, '#F59E0B'))
    charts.push(initChart(rankingChartRef.value, '排名', data.ranking_trend, '#BFDBFE', 'value'))

    // Invert ranking chart
    if (charts[4]) {
      charts[4].setOption({
        yAxis: {
          inverse: true
        }
      })
    }
  } catch (error) {
    ElMessage.error('加载历史数据失败：' + (error.response?.data?.detail || error.message))
  } finally {
    chartsLoading.value = false
  }
}

// Search products
const handleSearch = async (queryString, cb) => {
  if (!queryString || queryString.length < 1) {
    cb([])
    return
  }

  try {
    const results = await api.searchProducts(queryString, 10)
    cb(results)
  } catch (error) {
    console.error('搜索失败:', error)
    cb([])
  }
}

// Select product
const handleSelectProduct = (item) => {
  searchKeyword.value = ''
  currentProductId.value = item.product_id
  loadProductInfo(item.product_id)
  loadHistoryData()
}

// Clear product
const clearProduct = () => {
  currentProductId.value = null
  productInfo.value = {}
  charts.forEach(chart => chart.dispose())
  charts = []
}

// Date change
const handleDateChange = () => {
  loadHistoryData()
}

// Copy product ID
const copyProductId = async (productId) => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(productId)
      ElMessage.success('商品ID已复制')
      return
    }

    const textArea = document.createElement('textarea')
    textArea.value = productId
    textArea.style.position = 'fixed'
    textArea.style.left = '-9999px'
    document.body.appendChild(textArea)
    textArea.select()

    try {
      document.execCommand('copy')
      ElMessage.success('商品ID已复制')
    } finally {
      document.body.removeChild(textArea)
    }
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// Format number
const formatNumber = (num) => {
  if (!num && num !== 0) return '-'
  return num.toLocaleString()
}

// Handle resize
const handleResize = () => {
  charts.forEach(chart => chart.resize())
}

// Watch route query for productId
watch(() => route.query.productId, (newProductId) => {
  if (newProductId) {
    currentProductId.value = newProductId
    loadProductInfo(newProductId)
    loadHistoryData()
  } else {
    clearProduct()
  }
}, { immediate: true })

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  charts.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.product-detail-page {
  padding: var(--spacing-6);
  min-height: 100%;
}

/* ========== 空白状态 ========== */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
}

.empty-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-6);
}

.empty-icon {
  color: var(--color-primary);
  opacity: 0.3;
}

.empty-content h2 {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.empty-content p {
  font-size: var(--text-lg);
  color: var(--color-text-secondary);
  margin: 0;
}

:deep(.search-input .el-input__wrapper) {
  border-radius: var(--radius-xl);
  padding: var(--spacing-4) var(--spacing-5);
  box-shadow: var(--shadow-md);
}

/* ========== 详情内容 ========== */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

/* ========== 顶部导航 ========== */
.top-nav {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-5) var(--spacing-6);
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-6);
  flex-wrap: wrap;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  flex-shrink: 0;
}

.nav-title {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.nav-title h1 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.nav-title code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  background: var(--color-bg-tertiary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.nav-center {
  flex: 1;
  min-width: 200px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  flex-shrink: 0;
}

/* ========== 信息卡片 ========== */
.info-card {
  margin-bottom: var(--spacing-6);
}

.card-header,
.chart-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  font-weight: var(--font-bold);
}

.product-id-tag {
  font-family: 'Courier New', monospace;
  font-size: var(--text-sm);
  cursor: pointer;
  user-select: none;
  padding: var(--spacing-2) var(--spacing-3);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  background-color: var(--color-info-light);
  color: var(--color-info);
  transition: all var(--transition-base);
}

.product-id-tag:hover {
  background-color: var(--color-bg-hover);
  transform: translateY(-1px);
}

.product-id-tag .copy-icon {
  font-size: var(--text-sm);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.product-id-tag:hover .copy-icon {
  opacity: 1;
}

/* ========== 图表容器 ========== */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: var(--spacing-6);
}

.chart-card {
  height: 400px;
}

.chart {
  width: 100%;
  height: 320px;
}

/* ========== 搜索结果 ========== */
.search-result-item {
  padding: var(--spacing-3) 0;
}

.result-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.result-meta {
  display: flex;
  gap: var(--spacing-3);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.result-id {
  font-family: var(--font-mono);
  background: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .product-detail-page {
    padding: var(--spacing-4);
  }

  .top-nav {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-center,
  .nav-right {
    width: 100%;
  }

  .nav-right {
    flex-direction: column;
  }
}
</style>
