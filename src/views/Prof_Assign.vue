<template>
  <div class="container mt-5">
    <h2 class="mb-4">📝 교수용 과제 공지 목록</h2>

    <div class="d-flex justify-content-end mb-3">
      <button @click="toggleForm" class="btn btn-primary">
        {{ formVisible ? '✖ 닫기' : editingAssignmentId ? '✏ 수정 취소' : '➕ 새 과제 작성' }}
      </button>
    </div>

    <transition name="fade">
      <form
        v-if="formVisible"
        @submit.prevent="editingAssignmentId ? updateAssignment() : submitAssignment()"
        class="card card-body mb-4 shadow-sm"
      >
        <div class="mb-3">
          <label class="form-label">제목</label>
          <input v-model="title" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">설명</label>
          <textarea v-model="description" class="form-control" required></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">마감일</label>
          <input v-model="deadline" type="datetime-local" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">샘플 답안</label>
          <textarea v-model="sampleAnswer" class="form-control"></textarea>
        </div>
        <div class="mb-3" v-if="!editingAssignmentId">
          <label class="form-label">파일 첨부 (PDF)</label>
          <input type="file" class="form-control" @change="handleFileChange" accept="application/pdf" />
        </div>
        <button type="submit" class="btn btn-success">
          {{ editingAssignmentId ? '💾 수정 저장' : '📤 과제 등록' }}
        </button>
      </form>
    </transition>

    <div v-if="loading" class="d-flex align-items-center justify-content-center my-5">
      <strong role="status">불러오는 중...  </strong>
      <div class="spinner-border ms-3" aria-hidden="true"></div>
    </div>

    <div v-else-if="assignments.length === 0" class="alert alert-info">
      등록된 과제 공지가 없습니다.
    </div>

    <div v-else>
      <div v-for="assignment in assignments" :key="assignment.id" class="card mb-3 shadow-sm">
        <div class="card-body">
          <h5>{{ assignment.title }}</h5>
          <p class="text-muted">{{ assignment.description }}</p>
          <p>📅 마감일: <strong>{{ assignment.deadline ? formatDate(assignment.deadline) : 'N/A' }}</strong></p>

          <!-- 버튼 하단 정렬: 왼쪽(피드백) + 오른쪽(수정) -->
          <div class="d-flex justify-content-between align-items-center mt-3">
            <button class="btn btn-outline-primary btn-sm" @click="goToFeedback(assignment.id)">📄 피드백 보기</button>
            <button class="btn btn-outline-secondary btn-sm" @click="editAssignment(assignment)">✏ 수정</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const assignments = ref([])
const loading = ref(true)
const formVisible = ref(false)
const editingAssignmentId = ref(null)

const title = ref('')
const description = ref('')
const deadline = ref('')
const sampleAnswer = ref('')
const file = ref(null)

const formatDate = (datetime) => {
  if (!datetime) return 'N/A'
  const date = new Date(datetime)
  return isNaN(date.getTime()) ? 'N/A' : date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const fixDatetimeFormat = (dt) => {
  if (!dt) return ''
  return dt.length === 16 ? dt + ':00' : dt
}

const fetchAssignments = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('https://project2025-backend.onrender.com/assignments', {
      headers: { Authorization: `Bearer ${token}` },
    })
    assignments.value = res.data
  } catch (err) {
    console.error('❌ 과제 목록 불러오기 실패:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchAssignments)

const toggleForm = () => {
  formVisible.value = !formVisible.value
  if (!formVisible.value) clearForm()
}

const clearForm = () => {
  title.value = ''
  description.value = ''
  deadline.value = ''
  sampleAnswer.value = ''
  file.value = null
  editingAssignmentId.value = null
}

const handleFileChange = (e) => {
  file.value = e.target.files[0]
}

const submitAssignment = async () => {
  const formData = new FormData()
  const formattedDeadline = fixDatetimeFormat(deadline.value)
  console.log('📤 [제출] 마감일:', formattedDeadline)

  formData.append('title', title.value)
  formData.append('description', description.value)
  if (formattedDeadline) formData.append('deadline', formattedDeadline)
  formData.append('sample_answer', sampleAnswer.value)
  if (file.value) formData.append('file', file.value)

  try {
    const token = localStorage.getItem('access_token')
    await axios.post('https://project2025-backend.onrender.com/assignments/create', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    })
    alert('✅ 과제가 등록되었습니다.')
    formVisible.value = false
    clearForm()
    await fetchAssignments()
  } catch (err) {
    console.error('❌ 과제 생성 실패:', err.response?.data || err)
    alert(`오류 발생: ${err.response?.data?.detail || '서버 오류'}`)
  }
}

const editAssignment = (assignment) => {
  title.value = assignment.title
  description.value = assignment.description
  deadline.value = assignment.deadline?.slice(0, 16) || ''
  sampleAnswer.value = assignment.sample_answer || ''
  editingAssignmentId.value = assignment.id
  formVisible.value = true
}

const updateAssignment = async () => {
  const formattedDeadline = fixDatetimeFormat(deadline.value)
  console.log('🔧 [수정] 과제 ID:', editingAssignmentId.value)
  console.log('🔧 [수정] 마감일:', formattedDeadline)

  try {
    const token = localStorage.getItem('access_token')
    await axios.put(`https://project2025-backend.onrender.com/assignments/${editingAssignmentId.value}`, null, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      params: {
        title: title.value,
        description: description.value,
        deadline: formattedDeadline,
        sample_answer: sampleAnswer.value,
      },
    })
    alert('✅ 과제가 수정되었습니다.')
    formVisible.value = false
    clearForm()
    await fetchAssignments()
  } catch (err) {
    console.error('❌ 과제 수정 실패:', err.response?.data || err)
    alert(`오류 발생: ${err.response?.data?.detail || '서버 오류'}`)
  }
}

const goToFeedback = (id) => {
  router.push(`/professor/feedback/${id}`)
}
</script>

<style>
.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
