<template>
  <div class="container mt-5">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p class="mt-2">AI 피드백을 기다리는 중입니다...</p>
    </div>

    <div v-else-if="!feedback" class="alert alert-warning">
      아직 피드백을 받을 수 없습니다. 나중에 다시 시도해주세요.
    </div>

    <div v-else>
      <h2 class="mb-3">📋 피드백 결과: {{ feedback.assignmentTitle }}</h2>
      <p><strong>제출 파일:</strong> {{ feedback.filename }}</p>
      <p><strong>제출 시간:</strong> {{ feedback.submittedAt }}</p>

      <div class="mt-4">
        <h4>🧠 AI 피드백 요약</h4>
        <p class="text-muted">{{ feedback.summary }}</p>
      </div>

      <div class="mt-4">
        <h4>🔍 상세 피드백</h4>
        <ul class="list-group">
          <li class="list-group-item" v-for="(item, index) in feedback.details" :key="index">
            {{ item }}
          </li>
        </ul>
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

const route = useRoute()
const router = useRouter()
const submissionId = route.params.id

const feedback = ref(null)
const loading = ref(true)

const goBack = () => {
  router.push('/student/assignment')
}

onMounted(() => {
  // 백엔드가 없으므로 임시 데이터로 대체
  console.log('피드백 ID:', submissionId)
  setTimeout(() => {
    feedback.value = {
      assignmentTitle: '기말 프로젝트 보고서',
      filename: 'final_project.pdf',
      submittedAt: '2025-05-12 14:33',
      summary: '보고서의 구조는 전반적으로 명확하나 결론 부분의 설득력이 부족합니다.',
      details: [
        '서론은 명확하고 간결합니다.',
        '본론 2장의 논거가 더 보강되면 좋습니다.',
        '결론에 핵심 주장 요약이 빠져 있습니다.'
      ]
    }
    loading.value = false
  }, 1000)
})
</script>
