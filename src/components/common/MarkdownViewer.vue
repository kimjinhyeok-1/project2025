<template>
    <div>
      <div
        class="markdown-body"
        :style="{ maxHeight: expanded ? 'none' : '100px', overflow: expanded ? 'visible' : 'hidden' }"
        v-html="renderedHtml"
      ></div>
  
      <div v-if="isOverflowing" class="text-center mt-2">
        <button @click="toggleExpand" class="btn btn-primary btn-sm">
          {{ expanded ? '접기' : '더보기' }}
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  /* eslint-disable no-undef */
  
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
  const expanded = ref(false)
  const isOverflowing = ref(false)
  
  const md = new MarkdownIt({
    html: false,       // 보안 강화 (XSS 방지)
    linkify: true,      // URL 자동 링크화
    typographer: true,  // 더 나은 문장 부호
  })
  
  // 변환 + 오버플로우 체크
  const renderAndCheckOverflow = () => {
    renderedHtml.value = md.render(props.markdown)
    setTimeout(() => {
      const el = document.querySelector('.markdown-body')
      if (el && el.scrollHeight > 100) {
        isOverflowing.value = true
      } else {
        isOverflowing.value = false
      }
    }, 50)
  }
  
  const toggleExpand = () => {
    expanded.value = !expanded.value
  }
  
  onMounted(renderAndCheckOverflow)
  
  watch(() => props.markdown, () => {
    expanded.value = false
    renderAndCheckOverflow()
  })
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
  