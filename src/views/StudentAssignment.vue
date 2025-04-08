<template>
  <div class="container mt-5">
    <h2 class="mb-4">📋 과제 공지 목록</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
    </div>

    <div v-else-if="assignments.length === 0" class="alert alert-info">
      등록된 과제 공지가 없습니다.
    </div>

    <div v-else class="row g-4">
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
              <p class="card-text text-muted">{{ assignment.description }}</p>
              <p class="card-text">
                📅 마감일: <strong>{{ assignment.due }}</strong>
              </p>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const assignments = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/assignments') // 실제 API 주소로 교체
    assignments.value = res.data
  } catch (err) {
    console.error('과제 공지 로딩 실패:', err)
  } finally {
    loading.value = false
  }
})
</script>
