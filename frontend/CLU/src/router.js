import { createRouter, createWebHistory } from 'vue-router'
import LandingView from './views/LandingView.vue'
import PromptView from './views/PromptView.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView
  },
  {
    path: '/prompt',
    name: 'prompt',
    component: PromptView
    // Or lazy load: component: () => import('./views/PromptView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router // Export the router instance