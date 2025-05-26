<template>
  <div class="qna-wrapper">
    <div class="header-row">
      <h2 class="title">🤖 실시간 질문 확인</h2>
      <button class="btn btn-secondary" @click="loadLatestQuestions">🔄 질문 불러오기</button>
    </div>

    <!-- 질문 입력 창 -->
    <div class="question-input-container">
      <div class="input-row">
        <input
          v-model="newQuestion"
          class="input-area"
          type="text"
          placeholder="무엇이든 물어보세요"
        />
        <button class="search-button" @click="submitQuestion">
          🌐 검색
        </button>
      </div>
    </div>

    <!-- 질문 목록 -->
    <div>
      <div
        v-for="(q, idx) in questions"
        :key="idx"
        class="mb-4"
      >
        <div
          class="answer-wrapper"
          :class="{ 'selected-card': isSelected(idx) && !q.dummy }"
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
      newQuestion: "",
      questions: Array(5).fill({ text: "질문 로딩 중...", likes: 0, dummy: true })
    };
  },
  async mounted() {
    await this.loadLatestQuestions();
  },
  methods: {
    async loadLatestQuestions() {
      try {
        console.log("🔄 질문 ID 및 목록 불러오는 중...");
        const idRes = await fetch("https://project2025-backend.onrender.com/questions/latest_id");
        const idData = await idRes.json();
        this.q_id = parseInt(idData.q_id);
        console.log("✅ q_id 가져옴:", this.q_id);
        this.loadSelected();

        const questionsRes = await fetch("https://project2025-backend.onrender.com/questions/latest");
        const questionsData = await questionsRes.json();

        if (Array.isArray(questionsData.questions)) {
          console.log("✅ 질문 목록 수신:", questionsData.questions.length);
          this.questions = questionsData.questions.map(q => ({
            text: q.text,
            likes: q.likes ?? 0,
            dummy: false
          }));
        } else {
          console.warn("⚠️ 질문 목록이 배열이 아닙니다:", questionsData);
        }
      } catch (err) {
        console.error("❌ 질문 또는 q_id 불러오기 실패:", err);
      }
    },
    async submitQuestion() {
      const trimmed = this.newQuestion.trim();
      if (!trimmed || !this.q_id) {
        console.warn("⚠️ 질문 내용이 비어있거나 q_id 없음");
        alert("질문 내용을 입력해주세요.");
        return;
      }

      try {
        const payload = {
          q_id: this.q_id,
          text: trimmed
        };
        console.log("📤 질문 전송 요청:", payload);

        const res = await fetch("https://project2025-backend.onrender.com/student_question", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const msg = await res.text();
          throw new Error(`서버 응답 오류: ${res.status} ${msg}`);
        }

        console.log("✅ 질문 성공적으로 전송됨");
        this.newQuestion = "";
        await this.loadLatestQuestions();
      } catch (err) {
        console.error("❌ 질문 전송 실패:", err);
        alert("질문을 전송하는 데 실패했습니다.");
      }
    },
    isSelected(index) {
      return this.selected.includes(index);
    },
    toggleLike(index) {
      if (!this.q_id || isNaN(this.q_id)) {
        console.warn("❌ 유효하지 않은 q_id. 좋아요 요청 중단");
        return;
      }

      const alreadySelected = this.isSelected(index);
      const endpoint = alreadySelected ? "unlike" : "like";

      console.log(`📡 ${endpoint.toUpperCase()} 요청 전송 중... (index: ${index})`);

      fetch(`https://project2025-backend.onrender.com/question/${this.q_id}/${endpoint}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: index })
      }).then(() => {
        console.log(`✅ ${endpoint.toUpperCase()} 성공`);
        if (alreadySelected) {
          this.selected = this.selected.filter(i => i !== index);
        } else {
          this.selected = [...this.selected, index];
        }

        localStorage.setItem(
          `selected_questions_${this.q_id}`,
          JSON.stringify(this.selected)
        );
      }).catch(err => {
        console.error(`❌ ${endpoint.toUpperCase()} 실패:`, err);
      });
    },
    loadSelected() {
      const saved = localStorage.getItem(`selected_questions_${this.q_id}`);
      if (saved) {
        try {
          this.selected = JSON.parse(saved);
          console.log("📦 로컬 스토리지 선택 질문 불러오기:", this.selected);
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

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 950px;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.question-input-container {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
  width: 100%;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.input-area {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 2rem;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 600px;
  font-size: 1rem;
  border: 1px solid #ccc;
}

.search-button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.7rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #0056b3;
}

.answer-wrapper {
  position: relative;
  width: 100%;
  max-width: 950px;
  margin: 0.5rem auto;
  background-color: #f9fafb;
  padding: 0.75rem 1rem;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s ease, background-color 0.3s ease;
  cursor: pointer;
}

.answer-wrapper:hover {
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.selected-card {
  background-color: #a8cfff !important;
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #34495e;
  margin: 0;
}
</style>
