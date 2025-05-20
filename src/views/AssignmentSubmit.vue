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
      <p><strong>마감일:</strong> {{ assignment.deadline }}</p>

      <!-- ✅ 이미 제출된 경우 안내 및 버튼 -->
      <div v-if="alreadySubmitted" class="alert alert-info d-flex justify-content-between align-items-center">
        <span>이 과제는 이미 제출되었습니다.</span>
        <button class="btn btn-outline-primary btn-sm" @click="goToFeedback">📄 피드백 다시 보기</button>
      </div>

      <!-- ✅ 제출 폼 -->
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

        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ submitting ? '제출 중입니다...' : '제출하기' }}
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
const alreadySubmitted = ref(false)

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
    alert('📎 제출할 PDF 파일을 선택해주세요!')
    return
  }

  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('🔐 로그인이 필요합니다.')
    return
  }

  submitting.value = true

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    await axios.post(
      `https://project2025-backend.onrender.com/assignments/${assignmentId}/submit`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    alert('✅ 과제가 성공적으로 제출되었습니다. 피드백은 마감일 이후 확인할 수 있습니다.')
    alreadySubmitted.value = true
  } catch (err) {
    const msg = err.response?.data?.detail || err.message || '서버 오류 발생'
    if (msg.includes('마감일')) {
      alert('⏳ 마감일이 지나야 제출이 가능합니다.')
    } else {
      alert(`❌ 제출 실패: ${msg}`)
    }
    console.error('제출 에러:', err)
  } finally {
    submitting.value = false
  }
}

const goToFeedback = () => {
  if (!assignment.value?.deadline) {
    alert('❗ 마감일 정보가 없습니다.')
    return
  }

  const today = new Date()
  const dueDate = new Date(assignment.value.deadline)
  dueDate.setDate(dueDate.getDate() + 1) // 마감일 다음 날부터 가능

  if (today < dueDate) {
    alert('📅 과제 제출 마감일이 아직 지나지 않았습니다.')
    return
  }

  router.push(`/student/feedback/${assignmentId}`)
}

onMounted(async () => {
  try {
    const token = localStorage.getItem('access_token')

    const [assignmentRes, feedbackRes] = await Promise.all([
      axios.get(`https://project2025-backend.onrender.com/assignments/${assignmentId}`),
      axios.get(`https://project2025-backend.onrender.com/assignments/${assignmentId}/feedback`, {
        headers: { Authorization: `Bearer ${token}` }
      }).catch(() => null)
    ])

    assignment.value = assignmentRes.data
    alreadySubmitted.value = !!feedbackRes?.data?.feedback
  } catch (err) {
    console.error('데이터 불러오기 실패:', err)
  } finally {
    loading.value = false
  }
})
</script>
