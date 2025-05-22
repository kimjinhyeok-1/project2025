<template>
  <div class="container py-5">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p class="mt-3 text-muted">AI 피드백을 기다리는 중입니다...</p>
    </div>

    <div v-else-if="!parsedFeedback.length" class="alert alert-warning">
      피드백 데이터를 불러올 수 없습니다. 과제를 다시 제출하거나 나중에 시도해주세요.
    </div>

    <div v-else>
      <div class="bg-white shadow rounded-4 p-5">
        <h2 class="fw-bold mb-4">📋 AI 피드백 결과</h2>

        <div class="d-flex flex-column gap-4">
          <div
            v-for="(item, index) in parsedFeedback"
            :key="index"
            class="p-4 bg-light rounded-3 shadow-sm"
          >
            <h5 class="fw-semibold text-primary mb-2">{{ item.title }}</h5>
            <p v-html="formatContent(item.content)" class="mb-0 text-dark small lh-lg"></p>
          </div>
        </div>

        <div v-if="professorFeedback" class="mt-5 p-4 bg-warning-subtle rounded-3 shadow-sm">
          <h5 class="fw-bold text-warning mb-2">👨‍🏫 교수 피드백</h5>
          <p class="mb-0 text-dark small lh-lg">{{ professorFeedback }}</p>
        </div>

        <div class="mt-5 text-end">
          <button class="btn btn-outline-secondary" @click="goBack">← 돌아가기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const assignmentId = route.params.id
const loading = ref(true)
const parsedFeedback = ref([])
const professorFeedback = ref('') // ✅ 교수 피드백 상태 추가

const goBack = () => {
  router.push('/student/assignment')
}

// AI 피드백 텍스트 → 배열로 파싱
const parseFeedback = (text) => {
  if (!text) return []
  return text
    .split(/\n-\s+|^- /gm)
    .filter(Boolean)
    .map((section) => {
      const [title, ...rest] = section.split(':')
      return {
        title: title?.trim() || '제목 없음',
        content: rest.join(':').trim()
      }
    })
}

// ✅ Markdown → HTML 변환
const formatContent = (text) => {
  return marked.parse(text || '')
}

const fetchFeedback = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('🔐 로그인 정보가 없습니다. 다시 로그인해주세요.')
    router.push('/')
    return
  }

  try {
    const res = await axios.get(
      `https://project2025-backend.onrender.com/assignments/${assignmentId}/feedback`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )

    const feedbackRaw = res.data.feedback
    const profFeedbackRaw = res.data.professor_feedback // ✅ 교수 피드백

    if (!feedbackRaw) {
      alert('❗ 피드백 내용이 없습니다. 과제를 다시 제출해보세요.')
      return
    }

    parsedFeedback.value = parseFeedback(feedbackRaw)
    professorFeedback.value = profFeedbackRaw || '' // ✅ 값 할당
  } catch (err) {
    console.error('❌ 피드백 불러오기 실패:', err)
    alert('❌ 피드백을 불러오는 데 실패했습니다.\n마감일이 지나지 않았거나 제출 정보가 없을 수 있습니다.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchFeedback)
</script>
