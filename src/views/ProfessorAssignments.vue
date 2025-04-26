<template>
  <div class="container mt-5">
    <h2 class="mb-4">📝 교수용 과제 공지 목록</h2>

    <div class="d-flex justify-content-end mb-3">
      <router-link to="/professor/assignments/new" class="btn btn-primary">
        ➕ 새 과제 공지 작성
      </router-link>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="assignments.length === 0" class="alert alert-info">
      등록된 과제 공지가 없습니다.
    </div>

    <div v-else>
      <div
        v-for="assignment in assignments"
        :key="assignment.id"
        class="card mb-3 shadow-sm"
      >
        <div class="card-body">
          <h5>{{ assignment.title }}</h5>
          <p class="text-muted">{{ assignment.description }}</p>
          <p>📅 마감일: {{ assignment.due }}</p>
          <router-link :to="`/professor/assignments/${assignment.id}/submissions`" class="btn btn-outline-primary">
            제출 현황 보기
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

onMounted(async () => {
  try {
    const token = localStorage.getItem('access_token')

    const res = await axios.get('https://project2025-backend.onrender.com/assignments', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    assignments.value = res.data
  } catch (err) {
    console.error('❌ 과제 공지 불러오기 실패:', err)
  } finally {
    loading.value = false
  }
})
</script>
