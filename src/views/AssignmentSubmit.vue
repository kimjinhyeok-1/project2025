<template>
    <div class="container mt-5">
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status"></div>
      </div>
  
      <div v-else-if="!assignment" class="alert alert-danger">
        과제를 불러오는 데 실패했습니다.
      </div>
  
      <div v-else>
        <h2 class="mb-4">📝 과제 제출: {{ assignment.title }}</h2>
        <p class="text-muted">{{ assignment.description }}</p>
        <p><strong>마감일:</strong> {{ assignment.due }}</p>
  
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="file" class="form-label">파일 업로드</label>
            <input type="file" id="file" class="form-control" @change="handleFileChange" />
          </div>
  
          <div class="mb-3">
            <label for="note" class="form-label">추가 메모 (선택)</label>
            <textarea id="note" class="form-control" rows="3" v-model="note"></textarea>
          </div>
  
          <button type="submit" class="btn btn-primary">제출하기</button>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import axios from 'axios'
  
  const route = useRoute()
  const assignmentId = route.params.id
  
  const assignment = ref(null)
  const loading = ref(true)
  const selectedFile = ref(null)
  const note = ref('')
  
  const handleFileChange = (e) => {
    selectedFile.value = e.target.files[0]
  }
  
  const handleSubmit = async () => {
    alert('제출 기능은 백엔드 위치가 정해지면 연결될 예정입니다!')
    // 아래는 실제 백엔드가 생기면 쓸 코드
    /*
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('note', note.value)
  
    await axios.post(`https://project2025-backend.onrender.com/submit/${assignmentId}`, formData)
    */
  }
  
  onMounted(async () => {
    try {
      const res = await axios.get(`https://project2025-backend.onrender.com/assignments/${assignmentId}`)
      assignment.value = res.data
    } catch (err) {
      console.error('과제 정보 불러오기 실패:', err)
    } finally {
      loading.value = false
    }
  })
  </script>
  