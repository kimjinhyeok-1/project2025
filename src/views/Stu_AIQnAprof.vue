<template>
  <div class="qna-wrapper">
    <h2 class="title">궁금한 것이 무엇인가요?</h2>

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

    <!-- 스켈레톤 로딩 -->
    <div v-if="loading" class="skeleton-container">
      <div class="skeleton-text"></div>
      <div class="skeleton-text short"></div>
      <div class="skeleton-text"></div>
    </div>

    <!-- 답변 -->
    <div
      v-else-if="answerHtml"
      ref="answerSection"
      class="answer-wrapper"
    >
      <transition name="fade">
        <div v-html="showMore ? answerHtml : shortHtml" class="markdown-body"></div>
      </transition>

      <!-- 복사 버튼 (항상 표시) -->
      <button class="copy-button" @click="copyAnswer">
        📋 복사
      </button>

      <div v-if="isLongAnswer" class="more-button-wrapper">
        <button @click="toggleMore" class="more-button">
          {{ showMore ? "▲ 접기" : "▼ 더보기" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const backendBaseURL = process.env.NODE_ENV === 'production'
  ? 'https://project2025-backend.onrender.com'
  : '/api';

const question = ref('')
const answerHtml = ref('')
const shortHtml = ref('')
const loading = ref(false)
const showMore = ref(false)
const isLongAnswer = ref(false)
const answerSection = ref(null)

// ✅ 줄바꿈 breaks 확실히 true로 설정
const md = new MarkdownIt({
  breaks: true,
  linkify: true
})

const fetchAnswer = async () => {
  if (!question.value.trim()) return
  loading.value = true
  showMore.value = false
  try {
    const formData = new FormData()
    formData.append("question", question.value)

    const { data } = await axios.post(`${backendBaseURL}/assistant/ask`, formData)
    const html = md.render(data.answer || '')

    answerHtml.value = html
    isLongAnswer.value = html.length > 500
    shortHtml.value = isLongAnswer.value ? html.slice(0, 500) + '...' : html

    await nextTick()
    answerSection.value?.scrollIntoView({ behavior: 'smooth' })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const toggleMore = () => {
  showMore.value = !showMore.value
}

const copyAnswer = async () => {
  try {
    const temp = document.createElement('div')
    temp.innerHTML = answerHtml.value
    const text = temp.innerText
    await navigator.clipboard.writeText(text)
    alert('답변이 복사되었습니다.')
  } catch (err) {
    console.error('복사 실패:', err)
  }
}
</script>

<style scoped>
/* 기존 스타일에 맞춰 복사 버튼 위치/디자인 조정 필요 시 여기서 수정 가능 */
.copy-button {
  margin-top: 10px;
  background-color: transparent;
  border: none;
  color: #555;
  font-size: 14px;
  cursor: pointer;
}
.copy-button:hover {
  color: #000;
}
</style>
