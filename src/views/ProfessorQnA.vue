<template>
  <div class="container mt-5">
    <h2 class="text-center">❓ 질문 & 답변 확인하기</h2>

    <!-- 탭 -->
    <ul class="nav nav-tabs mt-4" style="justify-content: flex-start;">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'summary', 'text-primary': true }" @click="loadSummary">
          요약 보기
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'fullchat', 'text-primary': true }" @click="loadFullChat">
          전체 대화 보기
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'resources', 'text-primary': true }" @click="activeTab = 'resources'">
          자료 보기
        </a>
      </li>
    </ul>

    <!-- 내용 -->
    <div class="tab-content mt-3 border p-4 rounded bg-white shadow-sm">
      <!-- 요약 -->
      <div v-if="activeTab === 'summary'">
        <h5>📋 질문 요약</h5>
        <div v-if="summaryLoading" class="d-flex align-items-center">
          <strong role="status">불러오는 중...</strong>
          <div class="spinner-border ms-auto" aria-hidden="true"></div>
        </div>
        <p v-else>{{ summary }}</p>
      </div>

      <!-- 전체 대화 -->
      <div v-if="activeTab === 'fullchat'">
        <h5>💬 전체 대화 내용</h5>
        <div v-if="chatLoading" class="d-flex align-items-center">
          <strong role="status">불러오는 중...</strong>
          <div class="spinner-border ms-auto" aria-hidden="true"></div>
        </div>
        <ul v-else class="list-group">
          <li v-for="(msg, index) in fullChat" :key="index" class="list-group-item">
            <p><strong>🧑 학생 질문:</strong> {{ msg.question || '❌ 질문 없음' }}</p>
            <p><strong>🤖 GPT 답변:</strong> {{ msg.answer || '❌ 답변 없음' }}</p>
            <p class="text-muted small">{{ formatDate(msg.created_at) || '시간 정보 없음' }}</p>
          </li>
        </ul>

        <!-- 디버깅용 -->
        <pre class="mt-3 bg-light p-3 rounded small">
          {{ fullChat }}
        </pre>
      </div>

      <!-- 자료 보기 -->
      <div v-if="activeTab === 'resources'">
        <h5>📂 자료 보기</h5>
        <p>자료 기능은 추후 추가될 예정입니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getChatSummary, getChatLogs } from '@/api/professorService'

const activeTab = ref('summary')

const summary = ref('')
const fullChat = ref([])

const summaryLoading = ref(false)
const chatLoading = ref(false)

function formatDate(dateStr) {
  if (!dateStr) return ''
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
  activeTab.value = 'summary'
  summaryLoading.value = true
  try {
    const result = await getChatSummary()
    summary.value = result
  } catch (err) {
    summary.value = '❌ 요약 데이터를 불러올 수 없습니다.'
  } finally {
    summaryLoading.value = false
  }
}

const loadFullChat = async () => {
  activeTab.value = 'fullchat'
  chatLoading.value = true
  try {
    const result = await getChatLogs()
    console.log('📦 전체 대화 응답:', result) // ✅ 로그 추가!
    fullChat.value = Array.isArray(result) ? result : result.data || []
  } catch (err) {
    fullChat.value = []
    console.error('❌ 전체 대화 데이터 오류:', err)
  } finally {
    chatLoading.value = false
  }
}

// 최초 로딩 시 요약 탭 먼저 호출
loadSummary()
</script>

<style scoped>
.nav-link {
  cursor: pointer;
}
.tab-content {
  min-height: 200px;
}
pre {
  font-size: 0.8rem;
  color: #444;
}
</style>
