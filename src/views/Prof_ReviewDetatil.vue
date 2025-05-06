<template>
    <div class="detail-container text-start mt-5">
      <h3>📄 수업 요약 상세 보기</h3>
      <p class="text-muted">요약 ID: {{ id }}</p>
  
      <div v-if="summary" class="summary-content mt-4">
        <pre>{{ summary }}</pre>
      </div>
  
      <div v-else class="alert alert-warning mt-4">
        요약 내용을 불러오는 중입니다...
      </div>
  
      <button class="btn btn-secondary mt-4" @click="$router.back()">← 목록으로 돌아가기</button>
    </div>
  </template>
  
  <script>
  import { getSummaryById } from "@/api/snapshotService";
  
  export default {
    name: "ProfReviewDetail",
    data() {
      return {
        id: this.$route.params.id,
        summary: null,
      };
    },
    async mounted() {
      try {
        const data = await getSummaryById(this.id);
        this.summary = data.summary;
      } catch (error) {
        console.error("❌ 요약 상세 로딩 실패:", error);
        this.summary = "[요약을 불러올 수 없습니다.]";
      }
    },
  };
  </script>
  
  <style scoped>
  .detail-container {
    max-width: 900px;
    margin: auto;
    padding: 30px;
  }
  .summary-content {
    white-space: pre-wrap;
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
  }
  </style>
  