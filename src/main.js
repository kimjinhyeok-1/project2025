import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.min.css'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './assets/startbootstrap-sb-admin-2-master/css/sb-admin-2.css'

import axios from 'axios'

// ✅ 1. 모든 요청에 access_token 자동 설정
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ✅ 2. 쿠키 인증이 필요한 경우 CORS를 허용
axios.defaults.withCredentials = true  // << 이 설정 반드시 필요

// ✅ 3. 전역 앱 생성 및 라우터 연결
const app = createApp(App)
app.use(router)
app.mount('#app')
