import { createRouter, createWebHistory } from 'vue-router'
import LandingView from './views/LandingView.vue'
import PromptView from './views/PromptView.vue'
// Correctly import AboutView
import AboutView from './views/AboutView.vue'
// Import LicenseView
import LicenseView from './views/LicenseView.vue'

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
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView // Use the correct component variable
  },
  // Add the route for the License page
  {
    path: '/license',
    name: 'license',
    component: LicenseView // Use the imported LicenseView
  }
]

const router = createRouter({
  // Use environment variable for base URL, common in Vite projects
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router // Export the router instance