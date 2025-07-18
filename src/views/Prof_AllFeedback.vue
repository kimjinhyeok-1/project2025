<template>
  <div class="qna-wrapper">
    <h2 class="title">📊 전체 AI 피드백 목록</h2>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="answer-wrapper">
      <div class="spinner-border" role="status"></div>
      <p class="card-title">피드백을 불러오는 중입니다...</p>
    </div>

    <!-- 피드백 없음 -->
    <div v-else-if="feedbackList.length === 0" class="answer-wrapper card-title">
      아직 제출된 피드백이 없습니다.
    </div>

    <!-- 학생별 아코디언 카드 -->
    <div v-else>
      <div
        v-for="(entry, index) in feedbackList"
        :key="index"
        class="answer-wrapper"
      >
        <!-- 접기/펼치기 토글 헤더 -->
        <div
          class="card-text d-flex justify-content-between align-items-center"
          style="cursor: pointer"
          @click="toggle(entry.student_id)"
        >
          <span>👤 {{ entry.student_name }}</span>
          <span>{{ openId === entry.student_id ? '▲' : '▼' }}</span>
        </div>

        <!-- 펼쳐진 내용 영역 -->
        <div v-show="openId === entry.student_id">
          <div v-if="entry.gpt_feedback">
            <p class="card-text">📌 AI 피드백:</p>
            <MarkdownViewer :markdown="entry.gpt_feedback" />
          </div>
          <div v-else class="card-text">제출된 과제 없음.</div>

          <p class="card-text mt-3">👨‍🏫 교수 피드백:</p>
          <div v-if="entry.professor_feedback">{{ entry.professor_feedback }}</div>
          <div v-else class="card-text">작성된 교수 피드백 없음</div>

          <!-- 교수 피드백 작성 -->
          <div v-if="editingId === entry.student_id" class="card-text mt-2">
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
        </div>
      </div>
    </div>

    <!-- 돌아가기 버튼 -->
    <div class="card-text text-end mt-4" style="width: 950px;">
      <button class="btn btn-outline-secondary" @click="router.back()">← 돌아가기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import MarkdownViewer from '@/components/common/MarkdownViewer.vue'

const route = useRoute()
const router = useRouter()
const assignmentId = route.params.id

const loading = ref(true)
const feedbackList = ref([])
const editingId = ref(null)
const feedbackInputs = ref({})
const openId = ref(null) // 👈 현재 열린 학생 ID

const toggle = (studentId) => {
  openId.value = openId.value === studentId ? null : studentId
}

const startEditing = (studentId, current) => {
  editingId.value = studentId
  feedbackInputs.value[studentId] = current || ''
}

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

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}

.description-text {
  white-space: pre-line;
}
</style>
