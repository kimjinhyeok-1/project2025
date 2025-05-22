<template>
  <div class="qna-wrapper">
    <h2 class="title">🤖 실시간 질문 확인</h2>

    <div v-if="questions.length" class="question-list">
      <div v-for="(q, idx) in questions" :key="idx" class="question-tile">
        <div class="text">{{ q.text }}</div>
        <div class="meta">
          AI 생성 질문
          <button class="like-btn" @click="likeQuestion(idx)">👍 {{ q.likes }}</button>
        </div>
      </div>
    </div>
    <div v-else class="no-question">📭 아직 질문이 없습니다.</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      questions: [],
      q_id: null
    };
  },
  async mounted() {
    this.q_id = this.$route.query.q_id;
    if (!this.q_id) {
      console.warn("❌ q_id가 URL에 포함되어 있지 않습니다.");
      return;
    }
    await this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      try {
        const res = await fetch(`https://project2025-backend.onrender.com/questions/popular_likes?q_id=${this.q_id}`);
        const data = await res.json();
        console.log("📥 인기 질문 응답:", data);

        if (Array.isArray(data.results)) {
          this.questions = data.results.map(q => ({
            text: q.text,
            likes: q.likes || 0
          }));
        } else {
          this.questions = [];
        }
      } catch (err) {
        console.error("❌ 질문 조회 실패:", err);
        this.questions = [];
      }
    },

    async likeQuestion(questionIndex) {
      try {
        await fetch(`https://project2025-backend.onrender.com/question/${this.q_id}/like`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question_id: questionIndex })
        });
        this.questions[questionIndex].likes++;
      } catch (error) {
        console.error("❌ 좋아요 실패:", error);
      }
    }
  }
};
</script>

<style scoped>
.qna-wrapper { max-width: 800px; margin: 0 auto; padding: 2rem; }
.title { font-weight: bold; margin-bottom: 1rem; }
.question-list { margin-top: 1rem; }
.question-tile {
  background: white; border: 1px solid #dee2e6;
  border-radius: 0.5rem; padding: 1rem; margin-bottom: 0.75rem;
}
.question-tile .meta {
  font-size: 0.85rem; color: #6c757d; margin-top: 0.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.like-btn {
  background: none; border: none; cursor: pointer; color: #0d6efd;
  font-weight: bold; padding: 0.25rem 0.5rem;
}
.no-question {
  color: #6c757d; text-align: center; margin-top: 2rem;
}
</style>
