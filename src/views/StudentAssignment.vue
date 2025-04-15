<template>
  <div class="container mt-5">
    <h2 class="mb-4">📋 과제 공지 목록</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
    </div>

    <div v-else-if="assignments.length === 0" class="alert alert-info">
      등록된 과제 공지가 없습니다.
    </div>

    <div v-else>
      <div class="row g-4">
        <div
          v-for="assignment in assignments"
          :key="assignment.id"
          class="col-md-6"
        >
          <router-link
            :to="`/student/assignments/${assignment.id}`"
            class="text-decoration-none"
          >
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h5 class="card-title text-dark">{{ assignment.title }}</h5>
                <p class="card-text text-muted">
                  {{ truncateText(assignment.description, 100) }}
                </p>
                <p class="card-text">
                  📅 작성일: <strong>{{ formatDate(assignment.created_at) }}</strong>
                </p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

console.log("🧩 StudentAssignment 컴포넌트 로드됨")

const assignments = ref([])
const loading = ref(true)

// 날짜 포맷 함수
const formatDate = (datetime) => {
  return new Date(datetime).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 텍스트 요약 함수
const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

onMounted(async () => {
  console.log("🚀 StudentAssignment onMounted 진입")
  try {
    const res = await axios.get('https://project2025-backend.onrender.com/assignments/')
    console.log('📦 과제 응답 데이터:', res.data)

    if (Array.isArray(res.data)) {
      assignments.value = res.data
    } else if (res.data && Array.isArray(res.data.assignments)) {
      assignments.value = res.data.assignments
    } else {
      console.warn('❗ 예상과 다른 데이터 구조:', res.data)
      assignments.value = []
    }
  } catch (err) {
    console.error('❌ 과제 공지 로딩 실패:', err)
    assignments.value = []
  } finally {
    loading.value = false
  }
})
</script>
