<template>
  <div class="selection-area">
    <!-- 筛选条件区域 -->
    <div class="filters-section">
      <div class="section-header">
        <div class="header-left">
          <el-icon class="header-icon"><Filter /></el-icon>
          <h2 class="section-title">筛选条件</h2>
        </div>
        <div class="header-actions">
          <el-button type="success" @click="showImportDialog" class="action-btn">
            <el-icon><Upload /></el-icon>
            <span>导入已调研商品</span>
          </el-button>
          <el-button type="warning" @click="showUnmarkDialog" class="action-btn">
            <el-icon><Download /></el-icon>
            <span>批量取消标记</span>
          </el-button>
          <el-button @click="handleReset" class="action-btn">
            <el-icon><RefreshLeft /></el-icon>
            <span>重置</span>
          </el-button>
          <el-button type="primary" @click="handleSearch" :loading="loading" class="action-btn cta-btn">
            <el-icon><Search /></el-icon>
            <span>查询商品</span>
          </el-button>
        </div>
      </div>

      <!-- 筛选表单 -->
      <div class="filters-grid">
        <!-- 活跃周期 -->
        <div class="filter-item">
          <label class="filter-label">活跃周期</label>
          <div class="input-group">
            <el-input-number
              v-model="filters.active_days"
              :min="1"
              :max="365"
              controls-position="right"
            />
            <span class="unit">天</span>
          </div>
        </div>

        <!-- 级联筛选 -->
        <div class="filter-item filter-item-wide">
          <label class="filter-label">类目筛选</label>
          <el-cascader
            v-model="filters.categories"
            :options="categoryOptions"
            :props="cascaderProps"
            placeholder="选择榜单 → 类目"
            clearable
            filterable
            class="full-width"
          />
        </div>

        <!-- 店铺类型 -->
        <div class="filter-item">
          <label class="filter-label">店铺类型</label>
          <el-select
            v-model="filters.shop_type"
            placeholder="全部"
            clearable
            class="full-width"
          >
            <el-option label="全托管" value="全托管" />
            <el-option label="半托管" value="半托管" />
          </el-select>
        </div>

        <!-- 调研状态 -->
        <div class="filter-item">
          <label class="filter-label">调研状态</label>
          <el-select
            v-model="filters.is_investigated"
            placeholder="全部"
            clearable
            class="full-width"
          >
            <el-option label="已调研" :value="true" />
            <el-option label="未调研" :value="false" />
          </el-select>
        </div>

        <!-- 总销量 -->
        <div class="filter-item">
          <label class="filter-label">总销量</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.total_sales_min"
              :min="0"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.total_sales_max"
              :min="0"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 日销量 -->
        <div class="filter-item">
          <label class="filter-label">日销量</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.daily_sales_min"
              :min="0"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.daily_sales_max"
              :min="0"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 7天平均日销 -->
        <div class="filter-item">
          <label class="filter-label">7天平均日销</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.avg_daily_sales_7d_min"
              :min="0"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.avg_daily_sales_7d_max"
              :min="0"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 评论数 -->
        <div class="filter-item">
          <label class="filter-label">评论数</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.comment_count_min"
              :min="0"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.comment_count_max"
              :min="0"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 留评率 -->
        <div class="filter-item">
          <label class="filter-label">留评率 (%)</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.review_rate_min"
              :min="0"
              :max="100"
              :precision="2"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.review_rate_max"
              :min="0"
              :max="100"
              :precision="2"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 价格 -->
        <div class="filter-item">
          <label class="filter-label">价格 ($)</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.price_min"
              :min="0"
              :precision="2"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.price_max"
              :min="0"
              :precision="2"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 类目排名 -->
        <div class="filter-item">
          <label class="filter-label">类目排名</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.level2_ranking_min"
              :min="1"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.level2_ranking_max"
              :min="1"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 监控次数 -->
        <div class="filter-item">
          <label class="filter-label">监控次数</label>
          <div class="range-inputs">
            <el-input-number
              v-model="filters.monitor_count_min"
              :min="0"
              placeholder="最小"
              controls-position="right"
              size="small"
            />
            <span class="separator">-</span>
            <el-input-number
              v-model="filters.monitor_count_max"
              :min="0"
              placeholder="最大"
              controls-position="right"
              size="small"
            />
          </div>
        </div>

        <!-- 排序字段 -->
        <div class="filter-item">
          <label class="filter-label">排序字段</label>
          <el-select
            v-model="filters.sort_by"
            placeholder="选择排序字段"
            class="full-width"
          >
            <el-option label="总销量" value="total_sales" />
            <el-option label="日销量" value="daily_sales" />
            <el-option label="评论数" value="comment_count" />
            <el-option label="价格" value="price" />
            <el-option label="排名" value="level2_ranking" />
            <el-option label="监控次数" value="monitor_count" />
          </el-select>
        </div>

        <!-- 排序顺序 -->
        <div class="filter-item">
          <label class="filter-label">排序顺序</label>
          <el-select
            v-model="filters.sort_order"
            class="full-width"
          >
            <el-option label="降序 (高到低)" value="desc" />
            <el-option label="升序 (低到高)" value="asc" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 商品列表区域 -->
    <div class="table-section">
      <div class="table-header">
        <div class="header-left">
          <el-icon class="header-icon"><List /></el-icon>
          <h3 class="table-title">商品列表</h3>
        </div>
        <div class="table-stats">
          <el-tag type="info" size="large">共 {{ total }} 条</el-tag>
        </div>
      </div>

      <div class="table-container" v-loading="loading">
        <el-table
          :data="tableData"
          stripe
          class="modern-table"
          @row-dblclick="handleRowDblClick"
        >
          <!-- 状态列 -->
          <el-table-column prop="is_investigated" label="状态" width="90" align="center" fixed="left">
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="row.is_investigated ? 'success' : 'info'"
                effect="plain"
              >
                {{ row.is_investigated ? '已调研' : '未调研' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="product_title" label="商品标题" min-width="300" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="product-title-cell">
                <span class="title-text">{{ row.product_title }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="类目" width="180">
            <template #default="{ row }">
              <div class="category-tags">
                <el-tag size="small" type="info">{{ row.category_level1 }}</el-tag>
                <el-tag size="small" type="warning">{{ row.category_level2 }}</el-tag>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="ranking_list" label="榜单" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="success">{{ row.ranking_list }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="shop_type" label="店铺" width="90" align="center">
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="row.shop_type === '全托管' ? 'primary' : 'warning'"
              >
                {{ row.shop_type }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="price" label="价格" width="100" sortable align="right">
            <template #default="{ row }">
              <span class="price-text">${{ row.price?.toFixed(2) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="daily_sales" label="日销" width="100" sortable align="right">
            <template #default="{ row }">
              <span class="metric-value primary">{{ formatNumber(row.daily_sales) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="total_sales" label="总销" width="110" sortable align="right">
            <template #default="{ row }">
              <span class="metric-value success">{{ formatNumber(row.total_sales) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="comment_count" label="评论" width="100" sortable align="right">
            <template #default="{ row }">
              <span class="metric-value warning">{{ formatNumber(row.comment_count) }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="review_rate" label="留评率" width="100" sortable align="center">
            <template #default="{ row }">
              <span class="rate-text">{{ row.review_rate ? row.review_rate + '%' : '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="level2_ranking" label="排名" width="90" sortable align="center">
            <template #default="{ row }">
              <span class="ranking-badge">{{ row.level2_ranking || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="product_id" label="商品ID" width="180">
            <template #default="{ row }">
              <div class="product-id-cell" @click="copyProductId(row.product_id)">
                <code class="mono-text">{{ row.product_id }}</code>
                <el-icon class="copy-icon"><CopyDocument /></el-icon>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                @click.stop="handleViewDetail(row)"
                class="action-button"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
          background
        />
      </div>
    </div>

    <!-- 导入已调研商品弹窗 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入已调研商品"
      width="600px"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <el-alert
        title="请输入商品ID，支持以下格式："
        type="info"
        :closable="false"
        show-icon
      >
        <ul class="help-list">
          <li>每行一个商品ID</li>
          <li>或用逗号分隔：ID1, ID2, ID3</li>
          <li>或用空格分隔：ID1 ID2 ID3</li>
        </ul>
      </el-alert>

      <el-input
        v-model="importInput"
        type="textarea"
        :rows="10"
        placeholder="请粘贴商品ID..."
        class="dialog-textarea"
      />

      <div class="dialog-footer-info">
        <el-tag type="info" size="large">
          已识别 {{ parsedProductIds.length }} 个商品ID
        </el-tag>
        <el-tag v-if="duplicatesCount > 0" type="warning" size="large">
          发现 {{ duplicatesCount }} 个重复ID，已自动去重
        </el-tag>
      </div>

      <template #footer>
        <div class="dialog-actions">
          <el-button @click="importDialogVisible = false" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="handleImportInvestigated"
            :loading="importLoading"
            :disabled="parsedProductIds.length === 0"
            size="large"
          >
            确认导入 ({{ parsedProductIds.length }})
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量取消调研标记弹窗 -->
    <el-dialog
      v-model="unmarkDialogVisible"
      title="批量取消调研标记"
      width="600px"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <el-alert
        title="请输入要取消调研标记的商品ID"
        type="warning"
        :closable="false"
        show-icon
      >
        <ul class="help-list">
          <li>这些商品将被标记为"未调研"</li>
          <li>支持与导入相同格式</li>
        </ul>
      </el-alert>

      <el-input
        v-model="unmarkInput"
        type="textarea"
        :rows="10"
        placeholder="请粘贴商品ID..."
        class="dialog-textarea"
      />

      <div class="dialog-footer-info">
        <el-tag type="info" size="large">
          已识别 {{ parsedUnmarkIds.length }} 个商品ID
        </el-tag>
      </div>

      <template #footer>
        <div class="dialog-actions">
          <el-button @click="unmarkDialogVisible = false" size="large">取消</el-button>
          <el-button
            type="danger"
            @click="handleUnmarkInvestigated"
            :loading="unmarkLoading"
            :disabled="parsedUnmarkIds.length === 0"
            size="large"
          >
            确认取消标记 ({{ parsedUnmarkIds.length }})
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument, Filter, List } from '@element-plus/icons-vue'

const router = useRouter()

// Dialog states
const importDialogVisible = ref(false)
const importInput = ref('')
const importLoading = ref(false)
const unmarkDialogVisible = ref(false)
const unmarkInput = ref('')
const unmarkLoading = ref(false)

// Filters
const filters = reactive({
  active_days: 30,
  categories: [],
  shop_type: null,
  is_investigated: null,
  sort_by: 'total_sales',
  sort_order: 'desc',
  total_sales_min: null,
  total_sales_max: null,
  daily_sales_min: null,
  daily_sales_max: null,
  avg_daily_sales_7d_min: null,
  avg_daily_sales_7d_max: null,
  comment_count_min: null,
  comment_count_max: null,
  review_rate_min: null,
  review_rate_max: null,
  price_min: null,
  price_max: null,
  monitor_count_min: null,
  monitor_count_max: null,
  level2_ranking_min: null,
  level2_ranking_max: null
})

// Pagination - 默认10条
const pagination = reactive({
  page: 1,
  page_size: 10
})

// Data
const tableData = ref([])
const total = ref(0)
const loading = ref(false)

// Category tree
const categoryOptions = ref([])
const cascaderProps = {
  value: 'name',
  label: 'name',
  children: 'children',
  expandTrigger: 'hover'
}

// Load category tree
const loadCategoryTree = async () => {
  try {
    const data = await api.getCategoryTree()
    categoryOptions.value = data.map(item => ({
      name: item.ranking_list,
      children: item.tree
    }))
  } catch (error) {
    ElMessage.error('加载类目树失败')
  }
}

// Search products
const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      ...filters,
      ranking_list: filters.categories[0] || undefined,
      category_level1: filters.categories[1] || undefined,
      category_level2: filters.categories[2] || undefined,
      page: pagination.page,
      page_size: pagination.page_size
    }

    // Remove null values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined || params[key] === '') {
        delete params[key]
      }
    })

    const data = await api.getProductList(params)
    tableData.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error('查询失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// Reset filters
const handleReset = () => {
  Object.assign(filters, {
    active_days: 30,
    categories: [],
    shop_type: null,
    is_investigated: null,
    sort_by: 'total_sales',
    sort_order: 'desc',
    total_sales_min: null,
    total_sales_max: null,
    daily_sales_min: null,
    daily_sales_max: null,
    avg_daily_sales_7d_min: null,
    avg_daily_sales_7d_max: null,
    comment_count_min: null,
    comment_count_max: null,
    review_rate_min: null,
    review_rate_max: null,
    price_min: null,
    price_max: null,
    monitor_count_min: null,
    monitor_count_max: null,
    level2_ranking_min: null,
    level2_ranking_max: null
  })
  pagination.page = 1
  handleSearch()
}

// View detail
const handleViewDetail = (row) => {
  // 切换到详情区并传递商品ID
  router.push({ path: '/main', query: { view: 'detail', productId: row.product_id } })
}

// Double click row
const handleRowDblClick = (row) => {
  handleViewDetail(row)
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

// Show import dialog
const showImportDialog = () => {
  importInput.value = ''
  importDialogVisible.value = true
}

// Show unmark dialog
const showUnmarkDialog = () => {
  unmarkInput.value = ''
  unmarkDialogVisible.value = true
}

// Parse product IDs
const parseProductIds = (input) => {
  if (!input || !input.trim()) {
    return []
  }

  const ids = input
    .split(/[\n,\s，]+/)
    .map(id => id.trim())
    .filter(id => id.length > 0)

  return [...new Set(ids)]
}

// Computed
const parsedProductIds = computed(() => {
  return parseProductIds(importInput.value)
})

const parsedUnmarkIds = computed(() => {
  return parseProductIds(unmarkInput.value)
})

const duplicatesCount = computed(() => {
  const allIds = importInput.value
    .split(/[\n,\s，]+/)
    .map(id => id.trim())
    .filter(id => id.length > 0)

  return allIds.length - parsedProductIds.value.length
})

// Import investigated
const handleImportInvestigated = async () => {
  if (parsedProductIds.value.length === 0) {
    ElMessage.warning('请输入商品ID')
    return
  }

  importLoading.value = true
  try {
    const result = await api.markProductsInvestigated(parsedProductIds.value, true)

    ElMessage.success({
      message: result.message || `成功标记 ${result.updated_count} 个商品为已调研`,
      duration: 3000
    })

    importDialogVisible.value = false
    handleSearch()
  } catch (error) {
    ElMessage.error('导入失败：' + (error.response?.data?.detail || error.message))
  } finally {
    importLoading.value = false
  }
}

// Unmark investigated
const handleUnmarkInvestigated = async () => {
  if (parsedUnmarkIds.value.length === 0) {
    ElMessage.warning('请输入商品ID')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将 ${parsedUnmarkIds.value.length} 个商品标记为"未调研"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  unmarkLoading.value = true
  try {
    const result = await api.markProductsInvestigated(parsedUnmarkIds.value, false)

    ElMessage.success({
      message: result.message || `成功取消 ${result.updated_count} 个商品的调研标记`,
      duration: 3000
    })

    unmarkDialogVisible.value = false
    handleSearch()
  } catch (error) {
    ElMessage.error('操作失败：' + (error.response?.data?.detail || error.message))
  } finally {
    unmarkLoading.value = false
  }
}

// Format number
const formatNumber = (num) => {
  if (!num && num !== 0) return '-'
  return num.toLocaleString()
}

onMounted(() => {
  loadCategoryTree()
  handleSearch()
})
</script>

<style scoped>
/* ========== 筛选区域 ========== */
.selection-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
  padding: var(--spacing-6);
  /* 移除固定高度和滚动限制，让内容自适应 */
}

.filters-section {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-6);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
  padding-bottom: var(--spacing-4);
  border-bottom: 2px solid var(--color-border-light);
  flex-wrap: wrap;
  gap: var(--spacing-4);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.header-icon {
  font-size: 24px;
  color: var(--color-primary);
}

.section-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-weight: var(--font-medium);
  transition: all var(--transition-base);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.cta-btn {
  background: linear-gradient(135deg, var(--color-cta) 0%, var(--color-cta-hover) 100%);
  border: none;
  color: white;
}

/* ========== 筛选表单网格 ========== */
.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.filter-item-wide {
  grid-column: span 2;
}

.filter-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.input-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.unit {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.range-inputs .el-input-number {
  flex: 1;
}

.separator {
  color: var(--color-text-tertiary);
  font-weight: var(--font-medium);
}

.full-width {
  width: 100%;
}

/* ========== 表格区域 ========== */
.table-section {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  /* 移除 flex: 1，让表格区域自适应内容高度 */
  display: flex;
  flex-direction: column;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-6);
  border-bottom: 1px solid var(--color-border-light);
}

.table-header .header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.table-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.table-container {
  /* 移除高度限制，让表格完全展示 */
  overflow-x: auto; /* 只保留横向滚动，纵向不限制 */
}

/* ========== 表格样式 ========== */
:deep(.modern-table .el-table__header) {
  background: var(--color-bg-tertiary);
}

:deep(.modern-table .el-table__header th) {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  font-size: var(--text-xs);
  letter-spacing: 0.05em;
  padding: var(--spacing-4) var(--spacing-3);
}

:deep(.modern-table .el-table__body tr) {
  transition: all var(--transition-fast);
  cursor: pointer;
}

:deep(.modern-table .el-table__body tr:hover) {
  background: var(--color-bg-hover) !important;
  transform: scale(1.005);
  box-shadow: var(--shadow-sm);
}

:deep(.modern-table .el-table__body td) {
  padding: var(--spacing-4) var(--spacing-3);
}

/* ========== 表格单元格 ========== */
.product-title-cell {
  display: flex;
  align-items: center;
}

.title-text {
  color: var(--color-text-primary);
  font-weight: var(--font-medium);
}

.category-tags {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.price-text {
  font-family: var(--font-mono);
  font-weight: var(--font-semibold);
  color: var(--color-success);
  font-size: var(--text-sm);
}

.metric-value {
  font-family: var(--font-mono);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
}

.metric-value.primary {
  color: var(--color-primary);
}

.metric-value.success {
  color: var(--color-success);
}

.metric-value.warning {
  color: var(--color-warning);
}

.rate-text {
  font-family: var(--font-mono);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

.ranking-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 24px;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}

.product-id-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.product-id-cell:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.mono-text {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-primary);
}

.copy-icon {
  font-size: 14px;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.product-id-cell:hover .copy-icon {
  opacity: 1;
}

.action-button {
  font-weight: var(--font-medium);
}

/* ========== 分页 ========== */
.pagination-wrapper {
  padding: var(--spacing-5) var(--spacing-6);
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--color-border-light);
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: var(--color-primary);
}

/* ========== 弹窗 ========== */
.help-list {
  margin: var(--spacing-3) 0 0 var(--spacing-5);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.help-list li {
  margin-bottom: var(--spacing-1);
}

.dialog-textarea {
  margin-top: var(--spacing-4);
}

.dialog-footer-info {
  margin-top: var(--spacing-4);
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .filters-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  .filter-item-wide {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .selection-area {
    padding: var(--spacing-4);
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    width: 100%;
  }

  .action-btn {
    flex: 1;
    justify-content: center;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }
}
</style>
