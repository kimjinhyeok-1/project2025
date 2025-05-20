<template>
  <div class="container py-5">
    <h2 class="mb-4 fw-bold">📊 전체 AI 피드백 목록</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p class="mt-3 text-muted">피드백을 불러오는 중입니다...</p>
    </div>

    <div v-else-if="feedbackList.length === 0" class="alert alert-info">
      아직 제출된 피드백이 없습니다.
    </div>

    <div v-else class="d-flex flex-column gap-4">
      <div
        v-for="(entry, index) in feedbackList"
        :key="index"
        class="p-4 bg-light rounded-3 shadow-sm"
      >
        <h5 class="text-primary mb-2">👤 학생 ID: {{ entry.student_id }}</h5>
        <div v-html="formatContent(entry.feedback)" class="small text-dark lh-lg"></div>
        <p class="text-muted mt-2 mb-0">🕒 생성일: {{ formatDate(entry.created_at) }}</p>
      </div>
    </div>

    <div class="mt-5 text-end">
      <button class="btn btn-outline-secondary" @click="router.back()">← 돌아가기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const assignmentId = route.params.id
const loading = ref(true)
const feedbackList = ref([])

const formatContent = (text) => {
  return text
    .replace(/\n\d+\.\s/g, '<br><strong>$&</strong>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

const formatDate = (dt) => {
  if (!dt) return 'N/A'
  const date = new Date(dt)
  return isNaN(date.getTime()) ? 'N/A' : date.toLocaleString('ko-KR')
}

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('🔐 로그인 정보가 없습니다.')
    router.push('/')
    return
  }

  try {
    const res = await axios.get(
      `https://project2025-backend.onrender.com/assignments/${assignmentId}/all-feedback`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    feedbackList.value = res.data || []
  } catch (err) {
    console.error('❌ 전체 피드백 로딩 실패:', err)
    alert('피드백 불러오기 실패. 제출된 정보가 없거나 권한이 없을 수 있습니다.')
  } finally {
    loading.value = false
  }
})
</script>
