<template>
  <div class="container mt-5">
    <h2 class="mb-2">🤖 AI 질문 보기 (학생용)</h2>
    <p class="text-muted">수업 중 생성된 AI 질문과 직접 작성한 질문을 모두 확인할 수 있습니다.</p>

    <!-- 질문 입력창 -->
    <div class="input-group mb-4">
      <input
        v-model="newQuestion"
        type="text"
        class="form-control"
        placeholder="Type your question"
        @keyup.enter="submitQuestion"
      />
      <button class="btn btn-primary" @click="submitQuestion">Submit</button>
    </div>

    <!-- 정렬 탭 -->
    <ul class="nav nav-tabs">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'popular' }" @click="tab = 'popular'">Popular</a>
      </li>
    </ul>

    <!-- 질문 목록 -->
    <div v-if="filteredQuestions.length" class="mt-3">
      <div v-for="(q, index) in filteredQuestions" :key="index" class="card mb-3">
        <div class="card-body d-flex justify-content-between align-items-center">
          <div>
            <p class="mb-1">{{ q.text }}</p>
            <small class="text-muted">Anonymous</small>
          </div>
          <button class="btn btn-sm btn-outline-primary" @click="likeQuestion(q.id)">
            👍 {{ q.likes }}
          </button>
        </div>
      </div>
    </div>
    <div v-else class="alert alert-info mt-4">아직 질문이 없습니다.</div>
  </div>
</template>

<script>
export default {
  name: 'StudentLessonQnA',
  data() {
    return {
      tab: 'recent',
      questions: [],
      newQuestion: ''
    }
  },
  computed: {
    filteredQuestions() {
      return [...this.questions].sort((a, b) => {
        if (this.tab === 'popular') return b.likes - a.likes;
        return new Date(b.created_at) - new Date(a.created_at);
      });
    }
  },
  mounted() {
    this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      try {
        const res = await fetch(`https://project2025-backend.onrender.com/questions`);
        this.questions = await res.json();
      } catch (err) {
        console.error('질문 로딩 실패:', err);
      }
    },
    async submitQuestion() {
      const text = this.newQuestion.trim();
      if (!text) return;

      try {
        const res = await fetch(`https://project2025-backend.onrender.com/questions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, source: 'student' })
        });
        const saved = await res.json();
        this.questions.unshift(saved);
        this.newQuestion = '';
      } catch (err) {
        console.error('질문 업로드 실패:', err);
      }
    },
    async likeQuestion(id) {
      try {
        await fetch(`https://project2025-backend.onrender.com/questions/${id}/like`, {
          method: 'PATCH'
        });
        const q = this.questions.find(q => q.id === id);
        if (q) q.likes++;
      } catch (err) {
        console.error('좋아요 실패:', err);
      }
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 0.75rem;
  box-shadow: 0 0 0.25rem rgba(0,0,0,0.1);
}
</style>
