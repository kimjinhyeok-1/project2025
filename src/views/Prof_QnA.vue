<template>
  <div class="container mt-5">
    <h2 class="text-center">❓ 질문 & 답변 확인하기</h2>

    <!-- 탭 -->
    <ul class="nav nav-tabs mt-4" style="justify-content: flex-start;">
      <li class="nav-item">
        <!-- ✅ 변경: 자동 호출 제거 -->
        <a
          class="nav-link"
          :class="{ active: activeTab === 'summary', 'text-primary': true }"
          @click="activeTab = 'summary'"
        >
          요약 보기
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'fullchat', 'text-primary': true }"
          @click="loadFullChat"
        >
          전체 대화 보기
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="{ active: activeTab === 'resources', 'text-primary': true }"
          @click="activeTab = 'resources'"
        >
          자료 보기
        </a>
      </li>
    </ul>

    <!-- 탭 내용 -->
    <div class="tab-content mt-3 border p-4 rounded bg-white shadow-sm">
      <!-- ✅ 요약 탭 -->
      <div v-if="activeTab === 'summary'">
        <h5>📋 질문 요약</h5>

        <!-- ✅ 버튼 추가: 요약이 없을 때만 보임 -->
        <button v-if="!summary.summary_for_professor && !summaryLoading" class="btn btn-primary mb-3" @click="loadSummary">
          📥 요약 불러오기
        </button>

        <div v-if="summaryLoading" class="d-flex align-items-center">
          <strong role="status">불러오는 중...</strong>
          <div class="spinner-border ms-auto" aria-hidden="true"></div>
        </div>

        <div v-else-if="summary.summary_for_professor">
          <h6>📝 요약 내용</h6>
          <p>{{ summary.summary_for_professor }}</p>

          <h6 class="mt-4">💡 자주 묻는 질문</h6>
          <ul>
            <li v-for="(q, index) in summary.most_common_questions" :key="index">
              {{ index + 1 }}. {{ q }}
            </li>
          </ul>
        </div>

        <div v-else-if="!summaryLoading">
          <p class="text-muted">📭 아직 요약을 불러오지 않았습니다.</p>
        </div>
      </div>

      <!-- ✅ 전체 대화 탭 -->
      <div v-if="activeTab === 'fullchat'">
        <h5>💬 전체 대화 내용</h5>

        <div v-if="chatLoading" class="d-flex align-items-center">
          <strong role="status">불러오는 중...</strong>
          <div class="spinner-border ms-auto" aria-hidden="true"></div>
        </div>

        <ul v-else class="list-group">
          <li
            v-for="(msg, index) in fullChat"
            :key="index"
            class="list-group-item"
          >
            <p><strong>🧑 질문:</strong> {{ msg.question }}</p>
            <p><strong>🤖 답변:</strong> {{ msg.answer }}</p>
            <p class="text-muted small">{{ formatDate(msg.created_at) }}</p>
          </li>
        </ul>

        <div v-if="fullChat.length === 0 && !chatLoading" class="text-muted mt-3">
          📭 아직 대화 기록이 없습니다.
        </div>
      </div>

      <!-- 자료 보기 탭 -->
      <div v-if="activeTab === 'resources'">
        <h5>📂 자료 보기</h5>
        <p>자료 기능은 추후 추가될 예정입니다.</p>
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
  } catch (error) {
    console.error('❌ 전체 대화 불러오기 실패:', error)
    fullChat.value = []
  } finally {
    chatLoading.value = false
  }
}

// ✅ 자동 호출 제거됨 (loadSummary 호출 X)
</script>

<style scoped>
.nav-link {
  cursor: pointer;
}
.tab-content {
  min-height: 200px;
}
</style>
