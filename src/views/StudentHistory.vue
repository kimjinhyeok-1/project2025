<template>
    <div class="container mt-5">
      <h2 class="mb-4">📚 내 대화 기록</h2>
  
      <div v-if="loading" class="d-flex align-items-center">
        <strong role="status">불러오는 중...</strong>
        <div class="spinner-border ms-auto" aria-hidden="true"></div>
      </div>
  
      <ul v-else class="list-group">
        <li
          v-for="(msg, index) in chatHistory"
          :key="index"
          class="list-group-item"
        >
          <p><strong>🧑 질문:</strong> {{ msg.question }}</p>
          <p><strong>🤖 답변:</strong> {{ msg.answer }}</p>
          <p class="text-muted small">{{ formatDate(msg.created_at) }}</p>
        </li>
      </ul>
  
      <div v-if="chatHistory.length === 0 && !loading" class="text-muted mt-3">
        📭 아직 대화 기록이 없습니다.
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  const chatHistory = ref([])
  const loading = ref(true)
  
  function formatDate(dateStr) {
    const d = new Date(dateStr)
    return d.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  onMounted(async () => {
    loading.value = true
  
    try {
      const token = localStorage.getItem('access_token')
      if (!token) throw new Error('토큰 없음')
  
      const response = await axios.get('https://project2025-backend.onrender.com/chat_history/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
  
      chatHistory.value = response.data || []
    } catch (error) {
      console.error('❌ 대화 기록 불러오기 실패:', error)
      chatHistory.value = []
    } finally {
      loading.value = false
    }
  })
  </script>
  