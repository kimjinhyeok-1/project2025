<template>
  <div class="container py-5">
    <h2 class="mb-4 fw-bold">📊 전체 AI 피드백 목록</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p class="mt-3 text-muted">피드백을 불러오는 중입니다...</p>
    </div>

    <div v-else-if="feedbackList.length === 0" class="alert alert-info">
      아직 제출된 피드백이 없습니다.
    </div>

    <div v-else class="d-flex flex-column gap-4">
      <div
        v-for="(entry, index) in feedbackList"
        :key="index"
        class="p-4 bg-light rounded-3 shadow-sm"
      >
        <h5 class="text-primary mb-2">👤 학생 ID: {{ entry.student_id }} - {{ entry.student_name }}</h5>

        <!-- AI 피드백 -->
        <div v-if="entry.gpt_feedback">
          <p class="mb-1 fw-bold">📌 AI 피드백:</p>
          <div v-html="formatContent(entry.gpt_feedback)" class="small text-dark lh-lg mb-2"></div>
        </div>
        <div v-else class="text-muted">제출된 과제 없음.</div>

        <!-- 교수 피드백 -->
        <div v-if="entry.gpt_feedback">
          <p class="mb-1 fw-bold">👨‍🏫 교수 피드백:</p>
          <div v-if="entry.professor_feedback">{{ entry.professor_feedback }}</div>
          <div v-else class="text-muted">작성된 교수 피드백 없음</div>

          <!-- 추가 피드백 작성 -->
          <div v-if="editingId === entry.student_id" class="mt-2">
            <textarea
              v-model="feedbackInputs[entry.student_id]"
              class="form-control mb-2"
              rows="3"
              placeholder="교수 피드백 입력"
            ></textarea>
            <button class="btn btn-sm btn-success me-2" @click="submitFeedback(entry.student_id)">저장</button>
            <button class="btn btn-sm btn-secondary" @click="editingId = null">취소</button>
          </div>
          <div v-else class="mt-2">
            <button class="btn btn-sm btn-outline-primary" @click="startEditing(entry.student_id, entry.professor_feedback)">
              ✍️ 추가 피드백 작성
            </button>
          </div>

          <p class="text-muted mt-2 mb-0">🕒 생성일: {{ formatDate(entry.gpt_feedback_time) }}</p>
        </div>
      </div>
    </div>

    <div class="mt-5 text-end">
      <button class="btn btn-outline-secondary" @click="router.back()">← 돌아가기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked' // ✅ Markdown 파서 추가

const route = useRoute()
const router = useRouter()
const assignmentId = route.params.id

const loading = ref(true)
const feedbackList = ref([])
const editingId = ref(null)
const feedbackInputs = ref({})

// ✅ Markdown -> HTML
const formatContent = (text) => {
  return marked.parse(text || '')
}

// 날짜 형식
const formatDate = (dt) => {
  if (!dt) return 'N/A'
  const date = new Date(dt)
  return isNaN(date.getTime()) ? 'N/A' : date.toLocaleString('ko-KR')
}

// 교수 피드백 입력 시작
const startEditing = (studentId, current) => {
  editingId.value = studentId
  feedbackInputs.value[studentId] = current || ''
}

// 교수 피드백 저장
const submitFeedback = async (studentId) => {
  const token = localStorage.getItem('access_token')
  const formData = new FormData()
  formData.append('feedback', feedbackInputs.value[studentId])

  try {
    await axios.post(
      `https://project2025-backend.onrender.com/assignments/${assignmentId}/student/${studentId}/professor-feedback`,
      formData,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    alert('✅ 교수 피드백이 저장되었습니다.')
    editingId.value = null
    await loadFeedbacks()
  } catch (err) {
    console.error('❌ 피드백 저장 실패:', err)
    alert('피드백 저장에 실패했습니다.')
  }
}

// 모든 피드백 로딩
const loadFeedbacks = async () => {
  const token = localStorage.getItem('access_token')
  try {
    const res = await axios.get(
      `https://project2025-backend.onrender.com/assignments/${assignmentId}/all-feedback`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    feedbackList.value = (res.data.feedbacks || []).sort((a, b) => a.student_id - b.student_id)
  } catch (err) {
    console.error('❌ 전체 피드백 로딩 실패:', err)
    alert('피드백 불러오기 실패. 제출된 정보가 없거나 권한이 없을 수 있습니다.')
  } finally {
    loading.value = false
  }
}

onMounted(loadFeedbacks)
</script>
