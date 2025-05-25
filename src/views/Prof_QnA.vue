<template>
  <div class="qna-wrapper">
    <h2 class="title">❓ 학생들의 질문</h2>

    <!-- 탭 -->
    <ul class="nav nav-tabs mt-4" style="justify-content: flex-start; width: 950px;">
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'summary', 'text-primary': true }"
          @click="activeTab = 'summary'"
        >
          SUMMARY
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'fullchat', 'text-primary': true }"
          @click="loadFullChat"
        >
          TOTAL
        </a>
      </li>
    </ul>

    <!-- 탭 내용 -->
    <div class="tab-content mt-3">
      <!-- 요약 탭 -->
      <div v-if="activeTab === 'summary'" class="answer-wrapper">
        <h5 class="card-title">📋 SUMMARY</h5>

        <button
          v-if="!summary.summary_for_professor && !summaryLoading"
          class="btn btn-primary mb-3"
          @click="loadSummary"
        >
          📥 요약 불러오기
        </button>

        <div v-if="summaryLoading" class="d-flex align-items-center justify-content-center my-3">
          <strong role="status">불러오는 중...</strong>
          <div class="spinner-border ms-3" aria-hidden="true"></div>
        </div>

        <div v-else-if="summary.summary_for_professor">
          <p class="card-text" style="white-space: pre-line;">{{ summary.summary_for_professor }}</p>
          <ul class="card-text mt-3">
            <li v-for="(q, index) in summary.most_common_questions" :key="index">
              {{ index + 1 }}. {{ q }}
            </li>
          </ul>
        </div>
      </div>

      <!-- 전체 대화 탭 -->
      <div v-if="activeTab === 'fullchat'" class="answer-wrapper">
        <h5 class="card-title">💬 전체 대화 내용</h5>

        <div v-if="chatLoading" class="d-flex align-items-center justify-content-center my-3">
          <strong role="status">불러오는 중...</strong>
          <div class="spinner-border ms-3" aria-hidden="true"></div>
        </div>

        <ul v-else class="list-unstyled">
          <li
            v-for="(msg, index) in fullChat"
            :key="index"
            class="card-text mb-4 border-bottom pb-3"
          >
            <p class="mb-1"><strong>🧑 질문:</strong> {{ msg.question }}</p>
            <p class="mb-1"><strong>🤖 답변:</strong> {{ msg.answer }}</p>
            <p class="text-muted small mb-0">{{ formatDate(msg.created_at) }}</p>
          </li>
        </ul>

        <div v-if="fullChat.length === 0 && !chatLoading" class="text-muted mt-3">
          📭 아직 대화 기록이 없습니다.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const activeTab = ref('summary')

const summary = ref({
  most_common_questions: [],
  summary_for_professor: '',
})
const fullChat = ref([])

const summaryLoading = ref(false)
const chatLoading = ref(false)
const hasLoadedChat = ref(false)

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

const loadSummary = async () => {
  summaryLoading.value = true

  try {
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('❌ 토큰 없음')

    const response = await axios.get('https://project2025-backend.onrender.com/chat_history/summary', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    summary.value = response.data
  } catch (error) {
    console.error('❌ 요약 데이터 불러오기 실패:', error)
    summary.value = {
      summary_for_professor: '⚠️ 요약 데이터를 불러올 수 없습니다.',
      most_common_questions: []
    }
  } finally {
    summaryLoading.value = false
  }
}

const loadFullChat = async () => {
  activeTab.value = 'fullchat'

  if (hasLoadedChat.value || chatLoading.value) return

  chatLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    if (!token) throw new Error('❌ 토큰 없음')

    const response = await axios.get('https://project2025-backend.onrender.com/chat_history/all', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    fullChat.value = response.data || []
    hasLoadedChat.value = true
  } catch (error) {
    console.error('❌ 전체 대화 불러오기 실패:', error)
    fullChat.value = []
  } finally {
    chatLoading.value = false
  }
}
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
  text-align: left;
  color: #2c3e50;
  width: 950px;
}

.tab-content {
  width: 950px;
}

.answer-wrapper {
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.answer-wrapper:hover {
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.card-text {
  font-size: 1.1rem;
  color: #34495e;
}

.text-muted {
  font-size: 0.9rem;
}
</style>
