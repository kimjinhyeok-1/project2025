<template>
  <div class="qna-wrapper">
    <h2 class="title">🤖 실시간 질문 하기</h2>

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
      <div v-for="(q, idx) in questions" :key="idx" class="question-tile">
        <div class="text">{{ q.text }}</div>
        <div class="meta">
          Anonymous · 🤖 AI 질문
          <button class="like-btn" @click="likeQuestion(q)">👍 {{ q.likes || 0 }}</button>
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
      questions: [],
      newQuestion: '',
      q_id: 12  // 실제 상황에서는 trigger_question_generation의 응답에서 받아야 함
    };
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
          const res = await fetch('https://project2025-backend.onrender.com/questions');
          const data = await res.json();
          console.log('📥 질문 응답:', data);

          const parsed = [];
          if (Array.isArray(data.results)) {
            data.results.forEach((entry) => {
              if (Array.isArray(entry.questions)) {
                entry.questions.forEach((q) => {
                  parsed.push({
                    text: q.text || q,
                    created_at: entry.created_at,
                    type: 'ai',
                    likes: q.likes || 0,
                    q_id: entry.q_id
                  });
                });
              }
            });
          }

          this.questions = parsed;
        } else if (this.tab === 'popular') {
          const res = await fetch(`https://project2025-backend.onrender.com/questions/popular_likes?q_id=${this.q_id}`);
          const data = await res.json();
          console.log("📥 인기 질문 응답:", data);

          if (Array.isArray(data.results)) {
            this.questions = data.results.map((q, idx) => ({
              id: idx,
              text: q.text,
              likes: q.likes || 0,
              created_at: new Date(),
              type: 'ai'
            }));
          } else {
            this.questions = [];
          }
        }
      } catch (err) {
        console.error('❌ 질문 조회 실패:', err);
        this.questions = [];
      }
    },

    async submitQuestion() {
      const text = this.newQuestion.trim();
      if (!text) return;

      try {
        const response = await fetch('https://project2025-backend.onrender.com/vad/student_question', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 1, text })
        });

        const data = await response.json();
        this.questions.unshift({
          id: Date.now(),
          text: data.text,
          created_at: data.created_at,
          type: 'student',
          likes: 0
        });
        this.newQuestion = '';
      } catch (err) {
        console.error('❌ 질문 제출 실패:', err);
      }
    },

    async likeQuestion(question) {
      try {
        const qid = question.q_id || this.q_id;
        await fetch(`https://project2025-backend.onrender.com/question/${qid}/like`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question_id: 0 }) // 인덱스 처리 필요 시 수정
        });
        question.likes = (question.likes || 0) + 1;
      } catch (err) {
        console.error('❌ 좋아요 실패:', err);
      }
    }
  }
};
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
