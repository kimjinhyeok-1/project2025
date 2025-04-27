<template>
  <div class="qna-wrapper">
    <h2 class="title">오늘은 무슨 생각을 하고 계신가요?</h2>

    <div class="input-area">
      <input
        v-model="question"
        type="text"
        placeholder="무엇이든 물어보세요"
        class="input-box"
        :disabled="loading"
        @keyup.enter="fetchAnswer"
      />
      <div class="icon-group">
        <button class="icon-button" @click="fetchAnswer" :disabled="loading">
          🌐 검색
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <div class="loading-text">답변을 가져오는 중...</div>
    </div>

    <div v-else-if="answerMarkdown" ref="answerSection">
      <MarkdownViewer :markdown="answerMarkdown" />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import MarkdownViewer from '@/components/common/MarkdownViewer.vue'

// ✅ 개발/배포 구분해서 backend 주소 다르게 처리
const backendBaseURL = process.env.NODE_ENV === 'production'
  ? 'https://project2025-backend.onrender.com'
  : '/api';

const question = ref('')
const answerMarkdown = ref('')
const loading = ref(false)
const answerSection = ref(null)

const fetchAnswer = async () => {
  if (!question.value.trim()) return
  loading.value = true
  try {
    const response = await axios.get(`${backendBaseURL}/ask_rag`, {
      params: {
        q: question.value,
        t: Date.now(),
      }
    })
    if (response.data && response.data.answer) {
      answerMarkdown.value = response.data.answer
      await nextTick()
      if (answerSection.value) {
        answerSection.value.scrollIntoView({ behavior: 'smooth' })
      }
    } else {
      answerMarkdown.value = '❗ 답변을 가져오는 데 실패했습니다. 다시 질문해 주세요.'
    }
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
  padding: 0.2rem 0.5rem;
  border-radius: 0.5rem;
  transition: background 0.2s;
}

.icon-button:hover:enabled {
  background: #f0f0f0;
}

.icon-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #000;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 1rem;
  font-size: 1rem;
  color: #666;
}
</style>
