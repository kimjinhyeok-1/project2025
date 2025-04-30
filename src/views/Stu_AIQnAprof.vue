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

      <!-- 복사 버튼 -->
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
/* 스타일 생략 – 기존 코드 유지 */
</style>
