import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 라우터 임포트
import '@fortawesome/fontawesome-free/css/all.min.css'

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import './assets/startbootstrap-sb-admin-2-master/css/sb-admin-2.css'
createApp(App).mount('#app')


import axios from 'axios'

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})


//console.log("환경 변수 체크:", process.env);
//console.log("VUE_APP_OPENAI_API_KEY:", process.env.VUE_APP_OPENAI_API_KEY);


const app = createApp(App);
app.use(router); // Vue 앱에 라우터 적용
app.mount('#app');
