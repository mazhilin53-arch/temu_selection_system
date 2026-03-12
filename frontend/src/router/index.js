import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 根路径直接显示主布局
  {
    path: '/',
    name: 'Home',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { title: 'Temu 选品系统' }
  },
  // 保留 /main 路径（兼容性）
  {
    path: '/main',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
