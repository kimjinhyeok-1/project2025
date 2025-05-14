<template>
  <div class="container mt-5">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p class="mt-2">AI 피드백을 기다리는 중입니다...</p>
    </div>

    <div v-else-if="!parsedFeedback.length" class="alert alert-warning">
      피드백 데이터를 불러올 수 없습니다.
    </div>

    <div v-else>
      <h2 class="mb-3">📋 AI 피드백 결과</h2>

      <div class="row row-cols-1 row-cols-md-2 g-4 mt-2">
        <div class="col" v-for="(item, index) in parsedFeedback" :key="index">
          <div class="card h-100 shadow-sm">
            <div class="card-body">
              <h5 class="card-title">{{ item.title }}</h5>
              <p class="card-text">{{ item.content }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4">
        <button class="btn btn-secondary" @click="goBack">돌아가기</button>
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

// 피드백 텍스트를 파싱해서 { title, content } 배열로 변환
const parseFeedback = (text) => {
  if (!text) return []
  return text
    .split(/\n-\s+/)
    .filter(Boolean)
    .map((section) => {
      const [title, ...rest] = section.split(':')
      return {
        title: title.trim(),
        content: rest.join(':').trim()
      }
    })
}

// 백엔드에서 피드백 가져오기
const fetchFeedback = async () => {
  const token = localStorage.getItem('access_token')
  try {
    const res = await axios.get(`https://project2025-backend.onrender.com/assignments/${assignmentId}/feedback`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    const feedbackRaw = res.data.feedback
    parsedFeedback.value = parseFeedback(feedbackRaw)
  } catch (err) {
    console.error('❌ 피드백 불러오기 실패:', err)
    alert('피드백을 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchFeedback)
</script>
