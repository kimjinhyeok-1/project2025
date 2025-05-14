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
          <label for="file" class="form-label">파일 업로드 (PDF만 가능)</label>
          <input
            type="file"
            id="file"
            class="form-control"
            accept=".pdf"
            @change="handleFileChange"
          />
        </div>

        <button type="submit" class="btn btn-primary me-2" :disabled="submitting">
          {{ submitting ? '제출 중입니다...' : '제출하기' }}
        </button>

        <button type="button" class="btn btn-outline-secondary" @click="goToTestFeedback">
          피드백 테스트 보기
        </button>
      </form>
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

const assignment = ref(null)
const loading = ref(true)
const selectedFile = ref(null)
const submitting = ref(false)

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file && file.type !== 'application/pdf') {
    alert('📄 PDF 파일만 업로드할 수 있습니다!')
    e.target.value = ''
    selectedFile.value = null
    return
  }
  selectedFile.value = file
}

const handleSubmit = async () => {
  if (!selectedFile.value) {
    alert('파일을 선택해주세요!')
    return
  }

  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('로그인이 필요합니다.')
    return
  }

  submitting.value = true

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await axios.post(
      `https://project2025-backend.onrender.com/assignments/${assignmentId}/submit`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    const feedbackText = res.data.feedback
    alert('✅ 과제가 제출되었고 AI 피드백을 받았습니다!')

    // 피드백 페이지로 이동 + state로 전달
    router.push({
      path: `/student/feedback/${assignmentId}`,
      state: { feedback: feedbackText }
    })
  } catch (err) {
    const msg = err.response?.data?.message || '서버 오류 발생'
    alert(`❌ 제출 실패: ${msg}`)
    console.error('제출 에러:', err)
  } finally {
    submitting.value = false
  }
}

const goToTestFeedback = () => {
  const fakeId = 123
  router.push(`/student/feedback/${fakeId}`)
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
