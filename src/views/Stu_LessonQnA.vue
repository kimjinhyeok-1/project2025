<template>
  <div class="container mt-5">
    <h2 class="text-center mb-4">🤖 실시간 질문 확인</h2>

    <div class="text-center mb-4">
      <button class="btn btn-success" @click="loadLatestQuestions">🔄 질문 불러오기</button>
    </div>

    <div class="row">
      <div
        v-for="(q, idx) in questions"
        :key="idx"
        class="col-md-6 mb-4"
      >
        <div
          class="card shadow h-100 p-3"
          :class="{ 'bg-primary text-white': selected.includes(idx) }"
        >
          <div class="card-body">
            <p class="card-text">{{ q.text }}</p>
            <button
              class="btn btn-outline-primary mt-3"
              :class="{ 'btn-light text-primary': selected.includes(idx) }"
              :disabled="selected.includes(idx)"
              @click="selectQuestion(idx)"
            >
              {{ selected.includes(idx) ? '✅ 선택됨' : '선택하기' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      questions: [
        { text: "곧 AI가 질문을 생성합니다..." },
        { text: "이곳에 실시간 질문이 표시됩니다." }
      ],
      q_id: null,
      selected: []
    };
  },
  async mounted() {
    const qParam = this.$route.query.q_id;
    this.q_id = qParam ? parseInt(qParam) : null;
    if (this.q_id) {
      this.loadSelected();
      await this.fetchQuestionsById(this.q_id);
    }
  },
  methods: {
    async fetchQuestionsById(q_id) {
      try {
        const res = await fetch(`https://project2025-backend.onrender.com/questions/${q_id}`);
        const data = await res.json();
        if (Array.isArray(data.questions)) {
          this.questions = data.questions.map(q => ({ text: q.text }));
        }
      } catch (err) {
        console.error("질문 조회 실패:", err);
      }
    },
    async loadLatestQuestions() {
      try {
        const res = await fetch("https://project2025-backend.onrender.com/questions/latest");
        const data = await res.json();
        this.q_id = parseInt(data.q_id);
        if (Array.isArray(data.questions)) {
          this.questions = data.questions.map(q => ({ text: q.text }));
        }
        this.loadSelected();
      } catch (err) {
        console.error("최신 질문 불러오기 실패:", err);
      }
    },
    selectQuestion(index) {
      if (!this.q_id || isNaN(this.q_id)) {
        console.warn("❌ 유효하지 않은 q_id. 좋아요 요청 중단");
        return;
      }

      this.selected.push(index);
      localStorage.setItem(
        `selected_questions_${this.q_id}`,
        JSON.stringify(this.selected)
      );

      fetch(`https://project2025-backend.onrender.com/question/${this.q_id}/like`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: index })
      }).catch(err => console.error("선택 전송 실패:", err));
    },
    loadSelected() {
      const saved = localStorage.getItem(`selected_questions_${this.q_id}`);
      if (saved) {
        try {
          this.selected = JSON.parse(saved);
        } catch {
          this.selected = [];
        }
      }
    }
  }
};
</script>

<style scoped>
.card {
  transition: all 0.3s ease-in-out;
}
.card:hover {
  transform: scale(1.02);
}
</style>
