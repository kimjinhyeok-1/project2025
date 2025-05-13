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

        <button type="submit" class="btn btn-primary me-2">제출하기</button>

        <!-- 🧪 테스트용 피드백 보기 버튼 -->
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

  // 아직 백엔드가 없으므로 임시로 처리
  alert('✅ 과제가 성공적으로 제출되었습니다! AI 피드백 페이지로 이동합니다.')

  // 가짜 제출 ID (예: 123)로 피드백 페이지로 이동
  const fakeSubmissionId = 123
  router.push(`/student/feedback/${fakeSubmissionId}`)

  // 실제 백엔드가 생기면 아래 코드로 교체 예정
  /*
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await axios.post(`https://project2025-backend.onrender.com/submit/${assignmentId}`, formData)
    const submissionId = res.data.submissionId
    router.push(`/student/feedback/${submissionId}`)
  } catch (err) {
    console.error('제출 실패:', err)
    alert('❌ 과제 제출에 실패했습니다. 다시 시도해주세요.')
  }
  */
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
