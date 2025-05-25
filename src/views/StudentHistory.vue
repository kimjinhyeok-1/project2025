<template>
  <div class="qna-wrapper">
    <h2 class="title">📚 내 대화 기록</h2>

    <div v-if="loading" class="d-flex align-items-center">
      <strong role="status">불러오는 중...</strong>
      <div class="spinner-border ms-auto" aria-hidden="true"></div>
    </div>

    <div
      v-else
      v-for="(msg, index) in chatHistory"
      :key="index"
      class="answer-wrapper"
    >
      <p class="card-text"><strong>🧑 질문:</strong> {{ msg.question }}</p>
      <p class="card-text">
        <strong>🤖 답변:</strong>
        <span v-html="renderMarkdown(msg.answer)" />
      </p>
      <p class="text-muted small">{{ formatDate(msg.created_at) }}</p>
    </div>

    <div v-if="chatHistory.length === 0 && !loading" class="card-text">
      📭 아직 대화 기록이 없습니다.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const chatHistory = ref([])
const loading = ref(true)
const md = new MarkdownIt()

function renderMarkdown(text) {
  return md.render(text || '')
}

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
      },
      withCredentials: true
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

<style scoped>
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: left;
  color: #2c3e50;
  width: 950px;
}

.answer-wrapper {
  position: relative;
  width: 950px;
  margin: 1rem auto;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.answer-wrapper:hover {
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}

.text-muted {
  font-size: 0.9rem;
}
</style>
