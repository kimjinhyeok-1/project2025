<template>
    <div>
      <div
        class="markdown-body"
        :style="{ maxHeight: expanded ? 'none' : '300px', overflow: expanded ? 'visible' : 'hidden' }"
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
  import { ref, onMounted, watch } from 'vue'
  import MarkdownIt from 'markdown-it'
  
  const props = defineProps({
    markdown: {
      type: String,
      required: true,
    },
  })
  
  const renderedHtml = ref('')
  const expanded = ref(false)
  const isOverflowing = ref(false)
  const containerRef = ref(null)
  
  const md = new MarkdownIt({
    html: false,
    linkify: true,
    typographer: true,
  })
  
  const toggleExpand = () => {
    expanded.value = !expanded.value
  }
  
  onMounted(() => {
    renderedHtml.value = md.render(props.markdown)
    checkOverflow()
  })
  
  watch(() => props.markdown, (newVal) => {
    renderedHtml.value = md.render(newVal)
    expanded.value = false
    checkOverflow()
  })
  
  const checkOverflow = () => {
    setTimeout(() => {
      const el = document.querySelector('.markdown-body')
      if (el && el.scrollHeight > 300) {
        isOverflowing.value = true
      } else {
        isOverflowing.value = false
      }
    }, 100)
  }
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
  