<template>
  <div class="qna-wrapper">
    <!-- 제목 + 버튼 -->
    <div class="title-bar d-flex justify-content-between align-items-center mb-3" style="width: 950px;">
      <h2 class="title">📝 교수용 과제 공지 목록</h2>
      <button @click="toggleForm" class="btn btn-primary">
        {{ formVisible ? '✖ 닫기' : editingAssignmentId ? '✏ 수정 취소' : '➕ 새 과제 작성' }}
      </button>
    </div>

    <!-- 과제 작성 폼 -->
    <transition name="fade" class="answer-wrapper">
      <form
        v-if="formVisible"
        @submit.prevent="editingAssignmentId ? updateAssignment() : submitAssignment()"
        class="card-text card card-body mb-4 shadow-sm"
      >
        <div class="mb-3">
          <label class="form-label">제목</label>
          <input v-model="title" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">설명 (마크다운 지원)</label>
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

    <!-- 로딩 -->
    <div v-if="loading" class="card-text d-flex align-items-center justify-content-center my-5">
      <strong role="status">불러오는 중...  </strong>
      <div class="spinner-border ms-3" aria-hidden="true"></div>
    </div>

    <!-- 과제 없음 -->
    <div v-else-if="assignments.length === 0" class="card-text alert alert-info">
      등록된 과제 공지가 없습니다.
    </div>

    <!-- 과제 목록 -->
    <div v-else class="answer-wrapper">
      <div v-for="assignment in assignments" :key="assignment.id">
        <div>
          <h5 class="card-title">{{ assignment.title }}</h5>
          <!-- ✅ 마크다운으로 렌더링된 HTML 출력 -->
          <div class="card-text markdown-body" v-html="renderedDescriptions[assignment.id]"></div>
          <p>📅 마감일: <strong>{{ assignment.deadline ? formatDate(assignment.deadline) : 'N/A' }}</strong></p>

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
import MarkdownIt from 'markdown-it'

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

const renderedDescriptions = ref({})
const md = new MarkdownIt({ html: false, linkify: true, typographer: true })

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

const renderAllDescriptions = () => {
  renderedDescriptions.value = {}
  for (const assignment of assignments.value) {
    renderedDescriptions.value[assignment.id] = md.render(assignment.description || '')
  }
}

const fetchAssignments = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('https://project2025-backend.onrender.com/assignments', {
      headers: { Authorization: `Bearer ${token}` },
    })
    assignments.value = res.data
    renderAllDescriptions()
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

  try {
    const token = localStorage.getItem('access_token')
    const form = new URLSearchParams()
    form.append('title', title.value)
    form.append('description', description.value)
    form.append('sample_answer', sampleAnswer.value)
    if (formattedDeadline) form.append('deadline', formattedDeadline)

    await axios.put(
      `https://project2025-backend.onrender.com/assignments/${editingAssignmentId.value}`,
      form,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    )

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
  margin: 0;
  text-align: left;
  color: #2c3e50;
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

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}

.markdown-body {
  font-family: 'Noto Sans', sans-serif;
  line-height: 1.6;
  word-break: break-word;
  margin-bottom: 1rem;
}

.markdown-body pre {
  background-color: #f6f8fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body code {
  background-color: #f6f8fa;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}
</style>
