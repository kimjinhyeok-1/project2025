<template>
  <div class="container mt-5">
    <h2 class="mb-4">📝 교수용 과제 공지 목록</h2>

    <!-- 새 과제 작성 / 수정 폼 -->
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

    <!-- 로딩 -->
    <div v-if="loading" class="d-flex align-items-center justify-content-center my-5">
      <strong role="status">불러오는 중...  </strong>
      <div class="spinner-border ms-3" aria-hidden="true"></div>
    </div>

    <!-- 과제 없음 -->
    <div v-else-if="assignments.length === 0" class="alert alert-info">
      등록된 과제 공지가 없습니다.
    </div>

    <!-- 과제 목록 -->
    <div v-else>
      <div v-for="assignment in assignments" :key="assignment.id" class="card mb-3 shadow-sm">
        <div class="card-body">
          <h5>{{ assignment.title }}</h5>
          <p class="text-muted">{{ assignment.description }}</p>
          <p>📅 마감일: {{ assignment.deadline }}</p>
          <button class="btn btn-outline-secondary btn-sm mt-2" @click="editAssignment(assignment)">
            ✏ 수정
          </button>
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
const formVisible = ref(false)
const editingAssignmentId = ref(null)

const title = ref('')
const description = ref('')
const deadline = ref('')
const sampleAnswer = ref('')
const file = ref(null)

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
  if (!formVisible.value) {
    clearForm()
  }
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
  formData.append('title', title.value)
  formData.append('description', description.value)
  if (deadline.value) formData.append('deadline', deadline.value)
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
  deadline.value = assignment.deadline?.slice(0, 16) || '' // datetime-local 형식
  sampleAnswer.value = assignment.sample_answer || ''
  editingAssignmentId.value = assignment.id
  formVisible.value = true
}

const updateAssignment = async () => {
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
        deadline: deadline.value,
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
