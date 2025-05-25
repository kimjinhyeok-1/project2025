<template>
  <div class="qna-wrapper">
    <h2 class="title">🤖 실시간 질문 확인</h2>

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
          class="answer-wrapper"
          :class="{ 'bg-primary text-white': selected.includes(idx) && !q.dummy }"
        >
          <div class="card-body">
            <p class="card-text">{{ q.text }}</p>

            <!-- 버튼은 더미 아닐 때만 표시 -->
            <button
              v-if="!q.dummy"
              class="btn btn-outline-primary mt-3"
              :class="{ 'btn-light text-primary': selected.includes(idx) }"
              @click="toggleLike(idx)"
            >
              {{ selected.includes(idx) ? '✅ 선택 취소' : '선택하기' }}
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
      q_id: null,
      selected: [],
      questions: Array(5).fill({ text: "질문 로딩 중...", likes: 0, dummy: true })
    };
  },
  async mounted() {
    await this.loadLatestQuestions();
  },
  methods: {
    async loadLatestQuestions() {
      try {
        const idRes = await fetch("https://project2025-backend.onrender.com/questions/latest_id");
        const idData = await idRes.json();
        this.q_id = parseInt(idData.q_id);
        this.loadSelected();

        const questionsRes = await fetch("https://project2025-backend.onrender.com/questions/latest");
        const questionsData = await questionsRes.json();

        if (Array.isArray(questionsData.questions)) {
          this.questions = questionsData.questions.map(q => ({
            text: q.text,
            likes: q.likes ?? 0,
            dummy: false
          }));
        }
      } catch (err) {
        console.error("질문 또는 q_id 불러오기 실패:", err);
      }
    },
    toggleLike(index) {
      if (!this.q_id || isNaN(this.q_id)) {
        console.warn("❌ 유효하지 않은 q_id. 좋아요 요청 중단");
        return;
      }

      const alreadySelected = this.selected.includes(index);
      const endpoint = alreadySelected ? "unlike" : "like";
      const method = "PATCH";

      fetch(`https://project2025-backend.onrender.com/question/${this.q_id}/${endpoint}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: index })
      }).then(() => {
        if (alreadySelected) {
          this.selected = this.selected.filter(i => i !== index);
          if (this.questions[index].likes > 0) {
            this.questions[index].likes -= 1;
          }
        } else {
          this.selected.push(index);
          this.questions[index].likes += 1;
        }

        localStorage.setItem(
          `selected_questions_${this.q_id}`,
          JSON.stringify(this.selected)
        );
      }).catch(err => {
        console.error(`선택 ${endpoint} 전송 실패:`, err);
      });
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
/* ===== 기본 레이아웃 ===== */
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: left;
  color: #2c3e50;
  width: 950px;
}

/* ===== 카드 스타일 (과제 항목) ===== */
.answer-wrapper {
  position: relative;
  width: 450px;
  margin: 2rem auto;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.answer-wrapper:hover {
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}

.description-text {
  white-space: pre-line;
}
</style>
