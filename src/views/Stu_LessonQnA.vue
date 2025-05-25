<template>
  <div class="qna-wrapper">
    <!-- 타이틀 + 버튼을 한 줄에 정렬 -->
    <div class="header-row">
      <h2 class="title">🤖 실시간 질문 확인</h2>
      <button class="btn btn-secondary" @click="loadLatestQuestions">🔄 질문 불러오기</button>
    </div>

    <div>
      <div
        v-for="(q, idx) in questions"
        :key="idx"
        class="mb-4"
      >
        <div
          class="answer-wrapper"
          :class="{ 'selected-card': selected.includes(idx) && !q.dummy }"
          @click="toggleLike(idx)"
        >
          <div class="card-body">
            <p class="card-text">{{ q.text }}</p>
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

      fetch(`https://project2025-backend.onrender.com/question/${this.q_id}/${endpoint}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: index })
      }).then(() => {
        if (alreadySelected) {
          this.selected = this.selected.filter(i => i !== index);
        } else {
          this.selected.push(index);
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
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

/* 타이틀 + 버튼 배치용 */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 950px;
  margin-bottom: 1.5rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

/* 질문 카드 */
.answer-wrapper {
  position: relative;
  width: 100%;
  max-width: 950px;
  margin: 1rem auto;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 1.5rem 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease, background-color 0.3s ease;
  cursor: pointer;
}

.answer-wrapper:hover {
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

/* 선택된 카드 (더 눈에 띄는 색상) */
.selected-card {
  background-color: #a8cfff;
  box-shadow: 0 0 0 3px #7bb7ff inset;
}

/* 텍스트 */
.card-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #34495e;
  margin: 0;
}
</style>
