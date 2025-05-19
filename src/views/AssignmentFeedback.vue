<template>
  <div class="container py-5">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p class="mt-3 text-muted">AI 피드백을 기다리는 중입니다...</p>
    </div>

    <div v-else-if="!parsedFeedback.length" class="alert alert-warning">
      피드백 데이터를 불러올 수 없습니다. 과제를 다시 제출하거나 나중에 시도해주세요.
    </div>

    <div v-else>
      <h2 class="mb-4 fw-bold">📋 AI 피드백 결과</h2>

      <div class="d-flex flex-column gap-4">
        <div
          v-for="(item, index) in parsedFeedback"
          :key="index"
          class="card shadow-sm border-0"
        >
          <div class="card-body bg-light rounded">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title fw-semibold text-primary mb-0">{{ item.title }}</h5>
              <!-- 옵션 버튼 영역 필요시 여기에 -->
            </div>
            <p v-html="formatContent(item.content)" class="card-text text-dark small lh-lg mb-0"></p>
          </div>
        </div>
      </div>

      <div class="mt-5">
        <button class="btn btn-outline-secondary" @click="goBack">← 돌아가기</button>
      </div>
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
const loading = ref(true)
const parsedFeedback = ref([])

const goBack = () => {
  router.push('/student/assignment')
}

const parseFeedback = (text) => {
  if (!text) return []
  return text
    .split(/\n-\s+|^- /gm)
    .filter(Boolean)
    .map((section) => {
      const [title, ...rest] = section.split(':')
      return {
        title: title?.trim() || '제목 없음',
        content: rest.join(':').trim()
      }
    })
}

// 줄바꿈 및 강조 처리
const formatContent = (text) => {
  return text
    .replace(/\n\d+\.\s/g, '<br><strong>$&</strong>') // 번호 줄바꿈
    .replace(/\n/g, '<br>')                            // 일반 줄바꿈
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // **굵게**
}
const fetchFeedback = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('🔐 로그인 정보가 없습니다. 다시 로그인해주세요.')
    router.push('/')
    return
  }

  try {
    const res = await axios.get(
      `https://project2025-backend.onrender.com/assignments/${assignmentId}/feedback`,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )

    const feedbackRaw = res.data.feedback
    if (!feedbackRaw) {
      alert('❗ 피드백 내용이 없습니다. 과제를 다시 제출해보세요.')
      return
    }

    parsedFeedback.value = parseFeedback(feedbackRaw)
  } catch (err) {
    console.error('❌ 피드백 불러오기 실패:', err)
    alert('❌ 피드백을 불러오는 데 실패했습니다.\n마감일이 지나지 않았거나 제출 정보가 없을 수 있습니다.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchFeedback)
</script>
