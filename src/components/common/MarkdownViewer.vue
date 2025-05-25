<template>
  <div class="markdown-body" v-html="renderedHtml"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import MarkdownIt from 'markdown-it'

// props
const props = defineProps({
  markdown: {
    type: String,
    required: true,
  },
})

// 상태
const renderedHtml = ref('')

// 마크다운 렌더러
const md = new MarkdownIt({
  html: false,       // 보안 강화 (XSS 방지)
  linkify: true,      // URL 자동 링크화
  typographer: true,  // 더 나은 문장 부호
})

// 렌더 함수
const renderMarkdown = () => {
  renderedHtml.value = md.render(props.markdown)
}

onMounted(renderMarkdown)

watch(() => props.markdown, renderMarkdown)
</script>

<style scoped>
.markdown-body {
  font-family: 'Noto Sans', sans-serif;
  line-height: 1.6;
  word-break: break-word;
}

.markdown-body pre {
  background-color: #f6f8fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body code {
  background-color: #f6f8fa;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}
</style>
