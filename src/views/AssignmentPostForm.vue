<template>
    <div class="container mt-5" style="max-width: 700px;">
      <h2 class="mb-4">📝 새 과제 공지 작성</h2>
  
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label class="form-label">과제 제목</label>
          <input v-model="title" type="text" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label class="form-label">과제 설명</label>
          <textarea v-model="description" class="form-control" rows="4" required></textarea>
        </div>
  
        <div class="mb-3">
          <label class="form-label">마감일</label>
          <input v-model="due" type="date" class="form-control" required />
        </div>
  
        <button type="submit" class="btn btn-primary">공지 등록</button>
      </form>
  
      <div v-if="statusMessage" class="alert alert-info mt-3">
        {{ statusMessage }}
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router'
  
  const title = ref('')
  const description = ref('')
  const due = ref('')
  const statusMessage = ref('')
  const router = useRouter()
  
  const handleSubmit = async () => {
    if (!title.value || !description.value || !due.value) return
  
    try {
      await axios.post('http://localhost:8000/api/assignments', {
        title: title.value,
        description: description.value,
        due: due.value,
      })
  
      statusMessage.value = '✅ 공지가 성공적으로 등록되었습니다!'
      setTimeout(() => {
        router.push('/professor/assignments')
      }, 1000)
    } catch (err) {
      console.error('공지 등록 실패:', err)
      statusMessage.value = '❌ 공지 등록 중 오류가 발생했습니다.'
    }
  }
  </script>
  