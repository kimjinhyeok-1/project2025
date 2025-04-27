<template>
  <div class="container mx-auto p-6 bg-gray-50 min-h-screen">
    <h2 class="text-3xl font-bold text-gray-900 text-center mb-10">❓ 질문 & 답변 확인하기</h2>

    <!-- 탭 -->
    <div class="flex space-x-4 mb-8">
      <button
        class="px-6 py-2 rounded-full font-semibold"
        :class="activeTab === 'summary' ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 border border-blue-600'"
        @click="loadSummary"
      >
        요약 보기
      </button>
      <button
        class="px-6 py-2 rounded-full font-semibold"
        :class="activeTab === 'fullchat' ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 border border-blue-600'"
        @click="loadFullChat"
      >
        전체 대화 보기
      </button>
      <button
        class="px-6 py-2 rounded-full font-semibold"
        :class="activeTab === 'resources' ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 border border-blue-600'"
        @click="() => activeTab = 'resources'"
      >
        자료 보기
      </button>
    </div>

    <!-- 탭 내용 -->
    <div class="bg-white rounded-2xl shadow-md p-8">
      <!-- 요약 탭 -->
      <div v-if="activeTab === 'summary'">
        <h3 class="text-2xl font-bold text-gray-800 mb-6">📋 질문 요약</h3>

        <div v-if="summaryLoading" class="flex items-center space-x-2">
          <div class="w-6 h-6 border-4 border-blue-400 border-t-transparent border-solid rounded-full animate-spin"></div>
          <span class="font-semibold text-gray-600">불러오는 중...</span>
        </div>

        <div v-else>
          <div v-html="parsedMarkdown" class="prose max-w-none"></div>

          <h4 class="text-xl font-semibold text-gray-700 mt-8 mb-4">💡 자주 묻는 질문</h4>
          <ol class="list-decimal ml-6 text-gray-700 text-base">
            <li v-for="(q, index) in summary.most_common_questions" :key="index">
              {{ index + 1 }}. {{ q }}
            </li>
          </ol>
        </div>
      </div>

      <!-- 전체 대화 탭 -->
      <div v-if="activeTab === 'fullchat'">
        <h3 class="text-2xl font-bold text-gray-800 mb-6">💬 전체 대화 내용</h3>

        <div v-if="chatLoading" class="flex items-center space-x-2">
          <div class="w-6 h-6 border-4 border-blue-400 border-t-transparent border-solid rounded-full animate-spin"></div>
          <span class="font-semibold text-gray-600">불러오는 중...</span>
        </div>

        <div v-else>
          <div v-if="fullChat.length > 0" class="space-y-6">
            <div v-for="(msg, index) in fullChat" :key="index" class="bg-gray-100 p-4 rounded-lg">
              <p class="font-semibold text-gray-800">🧑 질문:</p>
              <p class="text-gray-700 mb-2">{{ msg.question }}</p>
              <p class="font-semibold text-gray-800">🤖 답변:</p>
              <p class="text-gray-700">{{ msg.answer }}</p>
              <p class="text-sm text-gray-500 mt-2">{{ formatDate(msg.created_at) }}</p>
            </div>
          </div>
          <div v-else class="text-center text-gray-400">
            📭 아직 대화 기록이 없습니다.
          </div>
        </div>
      </div>

      <!-- 자료 보기 탭 -->
      <div v-if="activeTab === 'resources'">
        <h3 class="text-2xl font-bold text-gray-800 mb-6">📂 자료 보기</h3>
        <p class="text-gray-600">자료 기능은 추후 추가될 예정입니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const activeTab = ref('summary')
const summary = ref({
  most_common_questions: [],
  summary_for_professor: '',
})
const fullChat = ref([])
const summaryLoading = ref(false)
const chatLoading = ref(false)

const parsedMarkdown = computed(() => {
  return marked.parse(summary.value.summary_for_professor || '')
})

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
  activeTab.value = 'summary'
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

// 최초 로딩 시 요약 불러오기
loadSummary()
</script>

<style scoped>
.prose {
  max-width: 100%;
}
</style>
