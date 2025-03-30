<template>
    <div class="summary-detail text-center mt-5">
      <h2>📄 수업 요약 상세 보기</h2>
      <p class="text-muted">요약된 내용을 아래에서 확인하세요.</p>
  
      <div v-if="summary" class="summary-box mt-4 p-4">
        <h4>{{ summary.title }}</h4>
        <p><strong>🗓 날짜:</strong> {{ summary.date }}</p>
        <hr />
        <p style="white-space: pre-wrap; text-align: left;">{{ summary.content }}</p>
      </div>
  
      <div v-else>
        <p>요약 데이터를 불러오는 중입니다...</p>
      </div>
    </div>
  </template>
  
  <script>
  import { getSummaryById } from "@/api/sttService";
  
  export default {
    name: "ProfessorSummaryDetailView",
    data() {
      return {
        summary: null,
      };
    },
    async mounted() {
      const id = this.$route.params.id;
      try {
        this.summary = await getSummaryById(id);
      } catch (error) {
        console.error("요약 상세 조회 실패:", error);
      }
    },
  };
  </script>
  
  <style scoped>
  .summary-detail {
    max-width: 900px;
    margin: auto;
    padding: 30px;
  }
  .summary-box {
    background-color: #f8f9fa;
    border-radius: 12px;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
    text-align: left;
  }
  </style>
  