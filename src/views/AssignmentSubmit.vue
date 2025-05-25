<template>
  <div class="qna-wrapper">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
    </div>

    <div v-else-if="!assignment" class="alert alert-danger">
      과제를 불러오는 데 실패했습니다.
    </div>

    <div v-else class="answer-wrapper">
      <h2 class="title">📝 과제 제출: {{ assignment.title }}</h2>
      <hr class="my-divider" v-if="index !== Object.keys(sortedSummaries).length - 1" />
      <p class="card-text description-text">{{ assignment.description }}</p>
      <hr class="my-divider" v-if="index !== Object.keys(sortedSummaries).length - 1" />
      <p class="card-text"><strong>마감일:</strong> {{ assignment.deadline }}</p>

      <div v-if="alreadySubmitted" class="card-text alert alert-info d-flex justify-content-between align-items-center">
        <span>이 과제는 이미 제출되었습니다.</span>
        <button class="btn btn-outline-primary btn-sm" @click="goToFeedback">📄 피드백 다시 보기</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="card-text mb-3">
          <label for="file" class="form-label">파일 업로드 (PDF만 가능)</label>
          <input
            type="file"
            id="file"
            class="form-control"
            accept=".pdf"
            @change="handleFileChange"
          />
        </div>

        <button type="submit" class="card-text btn btn-primary" :disabled="submitting">
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
  dueDate.setDate(dueDate.getDate() + 1)

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

<style scoped>
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

.answer-wrapper {
  position: relative;
  width: 950px;
  margin: 1rem auto;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.answer-wrapper:hover {
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}

.text-muted {
  font-size: 0.9rem;
}

.description-text {
  white-space: pre-line;
}
</style>