<template>
  <div class="container py-4">
    <h2 class="mb-4">질문하기</h2>

    <!-- 질문 입력창 -->
    <div class="input-group mb-3">
      <input v-model="question" type="text" class="form-control" placeholder="질문을 입력하세요" @keyup.enter="fetchAnswer" />
      <button class="btn btn-primary" @click="fetchAnswer">질문하기</button>
    </div>

    <!-- 답변 영역 -->
    <div v-if="loading" class="text-center my-4">
      답변을 가져오는 중...
    </div>

    <div v-else-if="answerMarkdown">
      <h4 class="mt-4">답변</h4>
      <MarkdownViewer :markdown="answerMarkdown" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import MarkdownViewer from '@/components/common/MarkdownViewer.vue'

const question = ref('')
const answerMarkdown = ref('')
const loading = ref(false)

const fetchAnswer = async () => {
  if (!question.value.trim()) return

  loading.value = true
  try {
    const response = await axios.get('/ask_rag', { params: { q: question.value } })
    answerMarkdown.value = response.data.answer
  } catch (error) {
    console.error('답변 가져오기 실패:', error)
    answerMarkdown.value = '❗ 답변을 가져오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
}
</style>
