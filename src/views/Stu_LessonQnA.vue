<template>
  <div class="qna-wrapper">
    <h2 class="title">🤖 질문 게시판 (학생용)</h2>
    <p class="text-muted">GPT가 만든 질문과 직접 작성한 질문을 모두 확인할 수 있습니다.</p>

    <div class="input-area">
      <input
        v-model="newQuestion"
        type="text"
        class="input-box"
        placeholder="Type your question"
        @keyup.enter="submitQuestion"
      />
      <button class="icon-button" @click="submitQuestion">➤</button>
    </div>

    <div class="tab-group">
      <button :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</button>
      <button :class="{ active: tab === 'popular' }" @click="tab = 'popular'">Popular</button>
    </div>

    <div v-if="questions.length" class="question-list">
      <div v-for="(q, index) in questions" :key="index" class="question-tile">
        <div class="text">{{ q.text }}</div>
        <div class="meta">Anonymous · {{ q.type === 'student' ? '📌 학생 질문' : '🤖 AI 질문' }}</div>
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
      questions: [],
      newQuestion: ''
    }
  },
  mounted() {
    this.fetchQuestions();
  },
  watch: {
    tab() {
      this.fetchQuestions();
    }
  },
  methods: {
    async fetchQuestions() {
      try {
        if (this.tab === 'recent') {
          const res = await fetch('https://project2025-backend.onrender.com/vad/questions');
          const data = await res.json();
          this.questions = data.results.map(q => ({
            text: q.text,
            created_at: q.created_at,
            type: q.source || 'ai'
          }));
        } else if (this.tab === 'popular') {
          const res = await fetch('https://project2025-backend.onrender.com/vad/questions/popular_summary');
          const data = await res.json();
          this.questions = data.results.map(q => ({
            text: `${q.text} (${q.unknown_percent}%)`,
            created_at: new Date(),
            type: 'ai'
          }));
        }
      } catch (err) {
        console.error('질문 조회 실패:', err);
      }
    },
    async submitQuestion() {
      const text = this.newQuestion.trim();
      if (!text) return;

      try {
        const res = await fetch('https://project2025-backend.onrender.com/vad/student_question', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 1, text }) // 실제 user_id 필요
        });
        const data = await res.json();
        this.questions.unshift({
          text: data.text,
          created_at: data.created_at,
          type: 'student'
        });
        this.newQuestion = '';
      } catch (err) {
        console.error('질문 제출 실패:', err);
      }
    }
  }
}
</script>

<style scoped>
.qna-wrapper { max-width: 800px; margin: 0 auto; padding: 2rem; }
.title { font-weight: bold; }
.input-area { display: flex; margin-bottom: 1rem; gap: 0.5rem; }
.input-box {
  flex-grow: 1; padding: 0.5rem 1rem;
  border: 1px solid #ced4da; border-radius: 0.5rem;
}
.icon-button {
  padding: 0.5rem 1rem; background-color: #0d6efd;
  color: white; border: none; border-radius: 0.5rem;
}
.tab-group { display: flex; gap: 1rem; margin: 1rem 0; }
.tab-group button {
  padding: 0.5rem 1rem; border: none;
  background: #e9ecef; border-radius: 0.375rem; cursor: pointer;
}
.tab-group .active {
  background-color: #0d6efd; color: white;
}
.question-list { margin-top: 1rem; }
.question-tile {
  background: white; border: 1px solid #dee2e6;
  border-radius: 0.5rem; padding: 1rem; margin-bottom: 0.75rem;
}
.question-tile .meta {
  font-size: 0.85rem; color: #6c757d; margin-top: 0.5rem;
}
.no-question {
  color: #6c757d; text-align: center; margin-top: 2rem;
}
</style>
