<template>
    <div class="container mt-5">
      <h2>📄 수업 요약 상세보기</h2>
  
      <div v-if="loading" class="text-muted mt-3">요약을 불러오는 중입니다...</div>
  
      <div v-else-if="summary">
        <p><strong>🗓 날짜:</strong> {{ summary.date }}</p>
        <p><strong>📝 제목:</strong> {{ summary.title }}</p>
        <div class="mt-4 text-start">
          <h5>📘 요약 내용</h5>
          <p style="white-space: pre-line;">{{ summary.content }}</p>
        </div>
      </div>
  
      <div v-else class="alert alert-warning mt-3">
        ❗ 요약 정보를 불러올 수 없습니다.
      </div>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue'
  import { useRoute } from 'vue-router'
  
  const route = useRoute()
  const summary = ref(null)
  const loading = ref(true)
  
  const fetchSummaryDetail = async () => {
    try {
      const id = route.params.id
      const response = await fetch(`https://project2025-backend.onrender.com/summaries/${id}`)
      if (!response.ok) throw new Error('서버 응답 오류')
  
      const data = await response.json()
      summary.value = data
    } catch (error) {
      console.error('요약 상세 불러오기 실패:', error)
    } finally {
      loading.value = false
    }
  }
  
  onMounted(fetchSummaryDetail)
  </script>
  
  <style scoped>
  .container {
    background-color: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 0 8px rgba(0,0,0,0.1);
    max-width: 800px;
  }
  </style>
  