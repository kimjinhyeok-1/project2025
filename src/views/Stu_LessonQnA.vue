<!-- ==================== -->
<!-- 🎓 학생용 QnA 페이지 -->
<!-- ==================== -->
<template>
  <div class="qna-student">
    <h2>🤖 실시간 질문 확인</h2>
    <button @click="loadLatestQuestions">🔄 질문 불러오기</button>

    <div v-for="(q, idx) in questions" :key="idx" class="question-card" :class="{ selected: selected.includes(idx) }">
      <p>{{ q.text }}</p>
      <button @click="toggleLike(idx)">{{ selected.includes(idx) ? '✅ 선택 취소' : '선택하기' }}</button>
      <p class="likes">👍 {{ q.likes }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      questions: [],
      selected: [],
      q_id: null
    };
  },
  methods: {
    async loadLatestQuestions() {
      const idRes = await fetch("https://project2025-backend.onrender.com/questions/latest_id");
      const idData = await idRes.json();
      this.q_id = parseInt(idData.q_id);
      localStorage.setItem("latest_q_id", this.q_id);

      const res = await fetch("https://project2025-backend.onrender.com/questions/latest");
      const data = await res.json();
      this.questions = data.questions;

      const stored = localStorage.getItem(`selected_questions_${this.q_id}`);
      this.selected = stored ? JSON.parse(stored) : [];
    },
    async toggleLike(index) {
      const alreadySelected = this.selected.includes(index);
      const endpoint = alreadySelected ? "unlike" : "like";
      await fetch(`https://project2025-backend.onrender.com/question/${this.q_id}/${endpoint}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: index })
      });

      if (alreadySelected) {
        this.selected = this.selected.filter(i => i !== index);
        this.questions[index].likes -= 1;
      } else {
        this.selected.push(index);
        this.questions[index].likes += 1;
      }

      localStorage.setItem(`selected_questions_${this.q_id}`, JSON.stringify(this.selected));
    }
  },
  mounted() {
    this.loadLatestQuestions();
  }
};
</script>

<style scoped>
.qna-student {
  max-width: 800px;
  margin: auto;
  padding: 1rem;
}
.question-card {
  background: #f9f9f9;
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 10px;
  border: 1px solid #ddd;
}
.selected {
  background-color: #d0ebff;
}
.likes {
  font-size: 0.85rem;
  color: #555;
}
</style>
