<template>
  <div class="qna-wrapper">
    <h2 class="title">🤖 궁금한 것을 자유롭게 질문하세요</h2>
    <p class="text-muted">AI가 생성한 질문과 직접 작성한 질문이 함께 표시됩니다.</p>

    <div class="input-area">
      <input
        v-model="newQuestion"
        type="text"
        placeholder="Type your question"
        class="input-box"
        @keyup.enter="submitQuestion"
      />
      <button class="icon-button" @click="submitQuestion">➤</button>
    </div>

    <div class="tab-group">
      <button :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</button>
      <button :class="{ active: tab === 'popular' }" @click="tab = 'popular'">Popular</button>
    </div>

    <div v-if="filteredQuestions.length" class="question-list">
      <div v-for="q in filteredQuestions" :key="q.id" class="question-tile">
        <div class="text">{{ q.text }}</div>
        <div class="meta">
          <button class="like-btn" @click="likeQuestion(q.id)">👍 {{ q.likes }}</button> · Anonymous
        </div>
      </div>
    </div>
    <div v-else class="no-question">아직 질문이 없습니다.</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tab: 'recent',
      newQuestion: '',
      questions: []
    }
  },
  computed: {
    filteredQuestions() {
      return [...this.questions].sort((a, b) => {
        return this.tab === 'popular' ? b.likes - a.likes : new Date(b.created_at) - new Date(a.created_at);
      });
    }
  },
  mounted() {
    this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      const res = await fetch('https://project2025-backend.onrender.com/vad/trigger_question_generation');
      const data = await res.json();
      this.questions = data.results || data;
    },
    async submitQuestion() {
      const text = this.newQuestion.trim();
      if (!text) return;
      const res = await fetch('https://project2025-backend.onrender.com/vad/trigger_question_generation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, source: 'student' })
      });
      const saved = await res.json();
      this.questions.unshift(saved);
      this.newQuestion = '';
    },
    async likeQuestion(id) {
      await fetch(`https://project2025-backend.onrender.com/vad/trigger_question_generation/${id}/like`, {
        method: 'PATCH'
      });
      const q = this.questions.find(q => q.id === id);
      if (q) q.likes++;
    }
  }
}
</script>

<style scoped>
.qna-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}
.title {
  font-weight: bold;
}
.input-area {
  display: flex;
  margin-bottom: 1rem;
  gap: 0.5rem;
}
.input-box {
  flex-grow: 1;
  padding: 0.5rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 0.5rem;
}
.icon-button {
  padding: 0.5rem 1rem;
  background-color: #0d6efd;
  color: white;
  border: none;
  border-radius: 0.5rem;
}
.tab-group {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}
.tab-group button {
  padding: 0.5rem 1rem;
  border: none;
  background: #e9ecef;
  border-radius: 0.375rem;
  cursor: pointer;
}
.tab-group .active {
  background-color: #0d6efd;
  color: white;
}
.question-list {
  margin-top: 1rem;
}
.question-tile {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 0.75rem;
}
.question-tile .meta {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.like-btn {
  border: none;
  background: none;
  color: #0d6efd;
  cursor: pointer;
}
.no-question {
  color: #6c757d;
  text-align: center;
  margin-top: 2rem;
}
</style>
