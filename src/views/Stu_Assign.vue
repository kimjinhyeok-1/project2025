<template>
  <div class="qna-wrapper">
    <h2 class="title">📋 과제</h2>

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
            <div class="answer-wrapper">
              <h5 class="card-title text-dark">{{ assignment.title }}</h5>
              <p class="card-text text-muted description-text">
                {{ truncateText(assignment.description, 150) }}
              </p>
              <p class="card-text">
                📅 마감일:
                <strong>{{ assignment.deadline ? formatDate(assignment.deadline) : 'N/A' }}</strong>
              </p>
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

<style scoped>
/* ===== 기본 레이아웃 ===== */
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: left;
  color: #2c3e50;
  width: 950px;
}

/* ===== 카드 스타일 (과제 항목) ===== */
.answer-wrapper {
  position: relative;
  width: 950px;
  margin: 2rem auto;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 2rem;
  border-radius: 20px;
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
  line-height: 1.7;
  color: #34495e;
}

.description-text {
  white-space: pre-line;
}

</style>
