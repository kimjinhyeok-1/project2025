<template>
  <div class="container mt-5">
    <h2 class="mb-4">➕ 새 과제 공지 작성</h2>

    <form @submit.prevent="submitAssignment">
      <div class="mb-3">
        <label class="form-label">제목</label>
        <input v-model="title" type="text" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">설명</label>
        <textarea v-model="description" class="form-control" required></textarea>
      </div>

      <div class="mb-3">
        <label class="form-label">마감일 (예: 2025-05-01T23:59:00)</label>
        <input v-model="deadline" type="datetime-local" class="form-control" />
      </div>

      <div class="mb-3">
        <label class="form-label">샘플 답안</label>
        <textarea v-model="sampleAnswer" class="form-control"></textarea>
      </div>

      <div class="mb-3">
        <label class="form-label">파일 첨부 (PDF)</label>
        <input type="file" class="form-control" @change="handleFileChange" accept="application/pdf" />
      </div>

      <button type="submit" class="btn btn-primary">과제 생성</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const title = ref('')
const description = ref('')
const deadline = ref('')
const sampleAnswer = ref('')
const file = ref(null)

const router = useRouter()

const handleFileChange = (e) => {
  file.value = e.target.files[0]
}

const submitAssignment = async () => {
  const formData = new FormData()
  formData.append('title', title.value)
  formData.append('description', description.value)
  if (deadline.value) formData.append('deadline', deadline.value)
  formData.append('sample_answer', sampleAnswer.value)
  if (file.value) formData.append('file', file.value)

  try {
    const token = localStorage.getItem('access_token')
    await axios.post('https://project2025-backend.onrender.com/create', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    })

    alert('✅ 과제가 성공적으로 등록되었습니다.')
    router.push('/professor/assignments')
  } catch (err) {
    console.error('❌ 과제 생성 실패:', err.response?.data || err)
    alert(`오류 발생: ${err.response?.data?.detail || '서버 오류'}`)
  }
}
</script>
