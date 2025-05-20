<template>
  <div class="container mt-5">
    <h2 class="mb-4">📋 과제</h2>

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
          class="col-12" 
        >
          <router-link
            :to="`/student/assignments/${assignment.id}`"
            class="text-decoration-none"
          >
            <div class="card shadow-sm h-100">
              <div class="card-body p-4">
                <h5 class="card-title text-dark">{{ assignment.title }}</h5>
                <p class="card-text text-muted">
                  {{ truncateText(assignment.description, 150) }}
                </p>
                <p class="card-text">
                  📅 마감일:
                  <strong>{{ assignment.deadline ? formatDate(assignment.deadline) : 'N/A' }}</strong>
                </p>
                <!-- ❌ 작성일 제거 -->
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

const assignments = ref([])
const loading = ref(true)

const formatDate = (datetime) => {
  if (!datetime) return 'N/A'
  const date = new Date(datetime)
  return isNaN(date.getTime()) ? 'N/A' : date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

onMounted(async () => {
  try {
    const res = await axios.get('https://project2025-backend.onrender.com/assignments/')
    if (Array.isArray(res.data)) {
      assignments.value = res.data
    } else if (res.data && Array.isArray(res.data.assignments)) {
      assignments.value = res.data.assignments
    } else {
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
