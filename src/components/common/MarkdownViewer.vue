<template>
  <div class="markdown-body" v-html="renderedHtml"></div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'

export default {
  name: 'MarkdownViewer',
  props: {
    markdown: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const renderedHtml = ref('')

    const md = new MarkdownIt({
      html: false,       // 보안: HTML 차단
      linkify: true,     // URL 자동 링크
      typographer: true  // 따옴표 등 자동 수정
    })

    const renderMarkdown = () => {
      renderedHtml.value = md.render(props.markdown)
    }

    onMounted(renderMarkdown)

    watch(() => props.markdown, renderMarkdown)

    return {
      renderedHtml
    }
  }
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
