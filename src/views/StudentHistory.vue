<!-- src/views/StudentHistory.vue -->
<template>
    <div class="container mt-5">
      <h2 class="mb-4">📚 내 대화 기록</h2>
  
      <div v-if="loading" class="d-flex align-items-center">
        <strong role="status">Loading...</strong>
        <div class="spinner-border ms-auto" aria-hidden="true"></div>
      </div>
  
      <ul v-else class="list-group">
        <li
          v-for="(msg, index) in chatHistory"
          :key="index"
          class="list-group-item"
        >
          <strong>{{ msg.role === 'user' ? '나' : msg.role === 'assistant' ? 'GPT' : '시스템' }}:</strong>
          {{ msg.content }}
        </li>
      </ul>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  const chatHistory = ref([])
  const loading = ref(true)
  
  onMounted(async () => {
    try {
      const response = await axios.get('https://project2025-backend.onrender.com/api/chat/logs')
      chatHistory.value = response.data
    } catch (error) {
      console.error(error)
      chatHistory.value = [{ role: 'system', content: '❌ 대화 기록을 불러올 수 없습니다.' }]
    } finally {
      loading.value = false
    }
  })
  </script>
  