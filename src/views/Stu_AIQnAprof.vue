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
      @mouseenter="hovering = true"
      @mouseleave="hovering = false"
    >
      <transition name="fade">
        <div v-html="showMore ? answerHtml : shortHtml" class="markdown-body"></div>
      </transition>

      <!-- 복사 버튼 (호버 시만 표시) -->
      <button
        v-if="hovering"
        class="copy-button"
        @click="copyAnswer"
      >
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
const hovering = ref(false)

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

    const response = await axios.post(`${backendBaseURL}/ask_assistant`, formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    })

    if (response.data && response.data.answer) {
      const fullHtml = md.render(response.data.answer)
      answerHtml.value = fullHtml

      if (response.data.answer.length > 700) {
        isLongAnswer.value = true
        const shortText = response.data.answer.slice(0, 600) + "..."
        shortHtml.value = md.render(shortText)
      } else {
        isLongAnswer.value = false
        shortHtml.value = fullHtml
      }

      await nextTick()
      if (answerSection.value) {
        answerSection.value.scrollIntoView({ behavior: 'smooth' })
      }
    } else {
      answerHtml.value = '<p>❗ 답변을 가져오는 데 실패했습니다. 다시 질문해 주세요.</p>'
    }
  } catch (error) {
    console.error('답변 가져오기 실패:', error)
    answerHtml.value = '<p>❗ 답변을 가져오는 데 실패했습니다.</p>'
  } finally {
    loading.value = false
  }
}

const toggleMore = () => {
  showMore.value = !showMore.value
}

const copyAnswer = async () => {
  try {
    const tempElement = document.createElement('div')
    tempElement.innerHTML = showMore.value ? answerHtml.value : shortHtml.value
    const text = tempElement.innerText
    await navigator.clipboard.writeText(text)
    alert('✅ 답변이 복사되었습니다!')
  } catch (error) {
    alert('❗ 복사에 실패했습니다.')
  }
}
</script>

<style scoped>
/* ===== 기본 레이아웃 ===== */
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 2rem;
  text-align: center;
  color: #2c3e50;
}

/* ===== 입력창 스타일 ===== */
.input-area {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 2rem;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 600px;
}

/* input */
.input-box {
  flex: 1;
  border: none;
  font-size: 1rem;
  padding: 0.5rem;
  outline: none;
}

/* 버튼 */
.icon-group {
  display: flex;
  gap: 0.5rem;
  margin-left: 1rem;
}

.icon-button {
  background: #3498db;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: background 0.2s;
}

.icon-button:hover:enabled {
  background: #2980b9;
}

.icon-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ===== 답변 카드 ===== */
.answer-wrapper {
  position: relative;
  max-width: 950px; /* ✅ 카드 폭 넓힘 */
  margin: 4rem auto;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

/* 복사 버튼 */
.copy-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #3498db;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.answer-wrapper:hover .copy-button {
  opacity: 1;
  pointer-events: auto;
}

.copy-button:hover {
  background: #2980b9;
}

/* ===== 마크다운 스타일 ===== */
.markdown-body {
  font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
  font-size: 1.1rem;
  line-height: 2.0; /* ✅ 줄간격 늘림 */
  color: #333;
  word-break: break-word;
}

.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  font-weight: bold;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  color: #1f2d3d;
  font-size: 1.7rem;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.3rem;
}

.markdown-body p {
  margin: 1.2rem 0; /* ✅ 문단 간격 키움 */
}

.markdown-body ul {
  list-style: disc;
  padding-left: 1.5rem;
  margin: 1rem 0;
}

.markdown-body ul li {
  margin-bottom: 0.7rem;
}

/* 코드블럭 */
.markdown-body pre {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1.5rem 0;
}

.markdown-body code {
  background: #f6f8fa;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

/* ===== 트랜지션 효과 ===== */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
