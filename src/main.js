import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.min.css'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './assets/startbootstrap-sb-admin-2-master/css/sb-admin-2.css'

import axios from 'axios'

// ✅ 토큰 인터셉터 설정
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

axios.defaults.withCredentials = true // 👈 이거 추가 필요

// ✅ Vue 앱 생성 → 라우터 적용 → mount
const app = createApp(App)
app.use(router)
app.mount('#app')
