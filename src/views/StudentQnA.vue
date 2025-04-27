<template>
  <div class="qna-wrapper">
    <h2 class="title">오늘은 무슨 생각을 하고 계신가요?</h2>

    <div class="input-area">
      <input
        v-model="question"
        type="text"
        placeholder="무엇이든 물어보세요"
        class="input-box"
        @keyup.enter="fetchAnswer"
      />
    </div>

    <div v-if="loading" class="loading-text">답변을 가져오는 중...</div>
    <div v-else-if="answerMarkdown">
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
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

.title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 2rem;
  text-align: center;
}

.input-area {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 2rem;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 600px;
}

.input-box {
  flex: 1;
  border: none;
  font-size: 1rem;
  padding: 0.5rem;
  outline: none;
}

.icon-group {
  display: flex;
  gap: 0.5rem;
  margin-left: 1rem;
}

.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
}

.voice-group {
  margin-left: 0.5rem;
}

.voice-button {
  background: black;
  color: white;
  border: none;
  border-radius: 50%;
  width: 2.5rem;
  height: 2.5rem;
  font-size: 1.2rem;
  cursor: pointer;
}

.loading-text {
  margin-top: 2rem;
  font-size: 1rem;
  color: #666;
}
</style>
