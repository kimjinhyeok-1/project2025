<template>
  <div class="container py-5">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p class="mt-3 text-muted">AI 피드백을 기다리는 중입니다...</p>
    </div>

    <div v-else-if="!feedback" class="alert alert-warning">
      피드백 데이터를 불러올 수 없습니다. 과제를 다시 제출하거나 나중에 시도해주세요.
    </div>

    <div v-else>
      <div class="bg-white shadow rounded-4 p-5">
        <h2 class="fw-bold mb-4">📋 AI 피드백 결과</h2>

        <MarkdownViewer :markdown="feedback" />

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
import MarkdownViewer from '@/components/common/MarkdownViewer.vue'

const route = useRoute()
const router = useRouter()
const assignmentId = route.params.id

const loading = ref(true)
const feedback = ref('')
const professorFeedback = ref('')

const goBack = () => {
  router.push('/student/assignment')
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

    feedback.value = res.data.feedback || ''
    professorFeedback.value = res.data.professor_feedback || ''
  } catch (err) {
    console.error('❌ 피드백 불러오기 실패:', err)
    alert('❌ 피드백을 불러오는 데 실패했습니다.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchFeedback)
</script>
