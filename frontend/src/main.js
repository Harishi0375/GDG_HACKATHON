import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from '../src/router' // Import the router configuration

const app = createApp(App)

app.use(router) // Tell the Vue app to use the router

app.mount('#app')