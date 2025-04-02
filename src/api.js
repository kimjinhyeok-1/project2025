// 예시: src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL,  // ✅ Vue CLI 환경변수 접근법
});

export default api;
