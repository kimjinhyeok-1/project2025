<template>
  <div class="qna-wrapper">
    <h2 class="title">❓ 학생들의 질문</h2>

    <!-- 탭 -->
    <ul class="nav nav-tabs mt-4" style="justify-content: flex-start; width: 950px;">
      <li class="card-text nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'summary', 'text-primary': true }"
          @click="activeTab = 'summary'"
        >
          SUMMARY
        </a>
      </li>
      <li class="card-text nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'fullchat', 'text-primary': true }"
          @click="loadFullChat"
        >
          TOTAL
        </a>
      </li>
    </ul>

    <!-- SUMMARY -->
    <div class="tab-content mt-3">
      <div v-if="activeTab === 'summary'" class="answer-wrapper">
        <h5 class="card-title">📋 SUMMARY</h5>

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

      <!-- TOTAL -->
      <div v-if="activeTab === 'fullchat'" class="answer-wrapper">
        <h5 class="card-title">💬 전체 대화 목록</h5>

        <div v-if="chatLoading" class="d-flex align-items-center justify-content-center my-3">
          <strong role="status">불러오는 중...</strong>
          <div class="spinner-border ms-3" aria-hidden="true"></div>
        </div>

        <ul v-else class="list-unstyled">
          <li
            v-for="(msg, index) in fullChat"
            :key="index"
            class="py-3 border-bottom"
          >
            <!-- 드롭다운 토글 헤더 -->
            <div
              class="card-text d-flex justify-content-between align-items-center toggle-header"
              @click="toggle(index)"
              style="cursor: pointer"
            >
              <span class="question-text">🧑 질문: {{ msg.question }}</span>
              <span>{{ expanded[index] ? '▲' : '▼' }}</span>
            </div>

            <!-- 펼쳐진 답변 -->
            <div v-if="expanded[index]" class="mt-2">
              <div class="markdown-body" v-html="renderMarkdown(msg.answer)" />
              <p class="text-muted small mb-0">{{ formatDate(msg.created_at) }}</p>
            </div>
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const activeTab = ref('summary')

const summary = ref({
  most_common_questions: [],
  summary_for_professor: '',
})
const fullChat = ref([])
const expanded = ref([])

const summaryLoading = ref(false)
const chatLoading = ref(false)
const hasLoadedChat = ref(false)

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

const loadSummary = async () => {
  summaryLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get('https://project2025-backend.onrender.com/chat_history/summary', {
      headers: { Authorization: `Bearer ${token}` }
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
    const response = await axios.get('https://project2025-backend.onrender.com/chat_history/all', {
      headers: { Authorization: `Bearer ${token}` }
    })
    fullChat.value = response.data || []
    expanded.value = fullChat.value.map(() => false)
    hasLoadedChat.value = true
  } catch (error) {
    console.error('❌ 전체 대화 불러오기 실패:', error)
    fullChat.value = []
  } finally {
    chatLoading.value = false
  }
}

const toggle = (index) => {
  expanded.value[index] = !expanded.value[index]
}

onMounted(() => {
  loadSummary()
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

.toggle-header span {
  font-size: 1.05rem;
  font-weight: 500;
  color: #2c3e50;
}

.markdown-body {
  font-family: 'Noto Sans', sans-serif;
  line-height: 1.6;
  word-break: break-word;
  white-space: normal; /* ✅ 핵심 수정 */
}

.markdown-body p {
  margin: 0.4rem 0;
}


.markdown-body pre {
  background-color: #f6f8fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body code {
  background-color: #f6f8fa;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.question-text {
  padding-right: 5rem; /* 버튼과 겹치지 않도록 */
  word-break: break-word;
}
</style>
