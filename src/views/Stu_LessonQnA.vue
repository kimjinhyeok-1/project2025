<template>
    <div class="container mt-5">
      <h2>📄 강의 중 질문</h2>
      <p>이 페이지는 강의 중 AI가 생성한 질문을 보여줍니다.</p>
  
      <!-- ✅ 최초 불러오기 버튼 -->
      <button class="btn btn-primary mt-3" @click="fetchQuestions" v-if="!results.length && !loading">
        📥 질문 불러오기
      </button>
  
      <!-- ✅ 다시 불러오기 버튼 -->
      <div v-if="results.length && !loading" class="mb-3">
        <button class="btn btn-outline-primary" @click="fetchQuestions">
          🔄 최신 질문 다시 불러오기
        </button>
      </div>
  
      <!-- 로딩 상태 -->
      <div v-if="loading" class="text-muted mt-3">불러오는 중...</div>
  
      <!-- 결과 출력 -->
      <div v-if="results.length && !loading" class="mt-4">
        <div v-for="(item, index) in results" :key="index" class="card mb-4">
          <div class="card-body">
            <p class="font-weight-bold">{{ item.paragraph }}</p>
            <ul class="list-group list-group-flush mt-3">
              <li v-for="(question, qIndex) in item.questions" :key="qIndex" class="list-group-item">
                {{ question }}
              </li>
            </ul>
          </div>
        </div>
      </div>
  
      <!-- ✅ 질문이 없을 때 안내 메시지 -->
      <div v-else-if="!loading && !results.length" class="alert alert-info mt-4">
        🤖 질문이 아직 생성되지 않았습니다. <br />
        "질문 불러오기" 버튼을 눌러 확인해보세요!
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const results = ref([])
  const loading = ref(false)
  
  const fetchQuestions = async () => {
    loading.value = true
    try {
      const response = await fetch('https://project2025-backend.onrender.com/vad/upload_text_chunk')
      if (!response.ok) throw new Error('질문 불러오기 실패')
  
      const data = await response.json()
      results.value = data.results || []
    } catch (error) {
      console.error(error)
      alert('질문을 불러오는 데 실패했습니다.')
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style scoped>
  .container {
    background-color: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 0 8px rgba(0,0,0,0.1);
  }
  </style>
  