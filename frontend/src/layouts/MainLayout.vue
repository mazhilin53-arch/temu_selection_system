<template>
  <div class="main-layout">
    <!-- 左侧导航栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon :size="28"><ShoppingBag /></el-icon>
          <transition name="fade">
            <span class="logo-text" v-show="!isCollapsed">Temu 选品系统</span>
          </transition>
        </div>
      </div>

      <!-- 折叠按钮 - 作为导航项的一部分 -->
      <div class="collapse-trigger" @click="toggleCollapse" :title="isCollapsed ? '展开导航' : '折叠导航'">
        <el-icon class="collapse-icon">
          <component :is="isCollapsed ? 'DArrowRight' : 'DArrowLeft'" />
        </el-icon>
        <transition name="fade">
          <span class="collapse-text" v-show="!isCollapsed">{{ isCollapsed ? '展开' : '收起' }}</span>
        </transition>
      </div>

      <nav class="sidebar-nav">
        <div
          class="nav-item"
          :class="{ active: currentView === 'selection' }"
          @click="switchView('selection')"
        >
          <el-icon class="nav-icon"><Grid /></el-icon>
          <transition name="fade">
            <span class="nav-text" v-show="!isCollapsed">选品区</span>
          </transition>
        </div>

        <div
          class="nav-item"
          :class="{ active: currentView === 'detail' }"
          @click="switchView('detail')"
        >
          <el-icon class="nav-icon"><Document /></el-icon>
          <transition name="fade">
            <span class="nav-text" v-show="!isCollapsed">商品详情区</span>
          </transition>
        </div>
      </nav>

      <transition name="fade">
        <div class="sidebar-footer" v-show="!isCollapsed">
          <div class="footer-info">
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span>管理员</span>
            </div>
            <div class="info-item">
              <el-icon><Clock /></el-icon>
              <span>{{ currentTime }}</span>
            </div>
          </div>
        </div>
      </transition>
    </aside>

    <!-- 右侧内容区 -->
    <main class="main-content">
      <!-- 选品区 -->
      <SelectionArea v-if="currentView === 'selection'" />

      <!-- 商品详情区 -->
      <DetailArea v-else-if="currentView === 'detail'" />
    </main>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ShoppingBag, Grid, Document, User, Clock, DArrowLeft, DArrowRight } from '@element-plus/icons-vue'
import SelectionArea from '../views/SelectionArea.vue'
import DetailArea from '../views/DetailArea.vue'

const route = useRoute()
const router = useRouter()

const currentView = ref('selection')
const currentTime = ref('')
const isCollapsed = ref(false)
let timer = null

// Toggle sidebar collapse
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// Switch view
const switchView = (view) => {
  currentView.value = view

  // Update route query
  if (view === 'selection') {
    router.push({ path: '/main', query: {} })
  } else if (view === 'detail') {
    router.push({ path: '/main', query: { view: 'detail' } })
  }
}

// Watch route query changes to update view
watch(() => route.query, (query) => {
  if (query.view === 'detail' || query.productId) {
    currentView.value = 'detail'
  } else {
    currentView.value = 'selection'
  }
}, { immediate: true })

// Update time
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  // Update time every second
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
/* ========== 主布局 ========== */
.main-layout {
  display: flex;
  height: 100vh;
  background: #F5F5F5;
  overflow: hidden;
}

/* ========== 侧边栏 ========== */
.sidebar {
  width: 260px;
  background: var(--color-bg-secondary);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  z-index: var(--z-fixed);
  transition: width var(--transition-base);
}

.sidebar.collapsed {
  width: 80px;
}

/* ========== 折叠触发器 ========== */
.collapse-trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3) var(--spacing-5);
  margin: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.collapse-trigger:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.collapse-trigger .collapse-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.collapse-text {
  white-space: nowrap;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base), transform var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.sidebar.collapsed .collapse-trigger {
  padding: var(--spacing-3);
  justify-content: center;
}

.sidebar-header {
  padding: var(--spacing-6);
  padding-bottom: var(--spacing-4);
  border-bottom: none;
}

.sidebar.collapsed .sidebar-header {
  padding: var(--spacing-4);
  padding-bottom: var(--spacing-3);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-primary);
  border-radius: var(--radius-xl);
  color: white;
  transition: all var(--transition-base);
}

.sidebar.collapsed .logo {
  padding: var(--spacing-4);
  justify-content: center;
}

.logo .el-icon {
  font-size: 32px;
  color: white;
}

.logo-text {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: white;
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-3) var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.sidebar.collapsed .sidebar-nav {
  padding: var(--spacing-3);
  align-items: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  color: var(--color-text-secondary);
  font-weight: var(--font-medium);
}

.sidebar.collapsed .nav-item {
  padding: var(--spacing-4);
  justify-content: center;
}

.nav-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.sidebar.collapsed .nav-item:hover {
  transform: none;
}

.nav-item.active {
  background: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-md);
}

.nav-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.nav-text {
  font-size: var(--text-base);
  white-space: nowrap;
}

.sidebar-footer {
  padding: var(--spacing-6);
  border-top: 2px solid var(--color-border-light);
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.info-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  padding: var(--spacing-3);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-lg);
}

.info-item .el-icon {
  font-size: 16px;
  color: var(--color-primary);
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  overflow-y: auto; /* 改为自动纵向滚动 */
  display: flex;
  flex-direction: column;
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .sidebar {
    width: 220px;
  }

  .logo-text {
    font-size: var(--text-base);
  }

  .nav-text {
    font-size: var(--text-sm);
  }
}

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    flex-direction: row;
    align-items: center;
    padding: var(--spacing-4);
    box-shadow: var(--shadow-md);
  }

  .sidebar-header {
    border-bottom: none;
    padding: var(--spacing-2);
  }

  .logo {
    padding: var(--spacing-2) var(--spacing-4);
  }

  .sidebar-nav {
    flex-direction: row;
    padding: var(--spacing-2);
  }

  .sidebar-footer {
    display: none;
  }

  .nav-text {
    display: none;
  }

  .nav-item {
    padding: var(--spacing-3);
  }
}
</style>
