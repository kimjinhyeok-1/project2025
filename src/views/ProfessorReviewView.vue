<template>
    <div class="review-container text-center mt-5">
      <h2>📚 수업 복습 보기</h2>
      <p class="text-muted">이번 수업 동안 생성된 요약 목록입니다. 원하는 항목을 선택하여 상세 내용을 확인하세요.</p>
  
      <div v-if="summaries.length" class="mt-5">
        <div
          v-for="(item, index) in summaries"
          :key="index"
          class="review-item mb-4 p-3"
        >
          <p><strong>🗓 날짜:</strong> {{ item.date }}</p>
          <p><strong>📝 주차 요약 제목:</strong> {{ item.title }}</p>
          <router-link :to="`/professor/review/${item.id}`" class="btn btn-outline-primary mt-2">
            📄 요약 보기
          </router-link>
        </div>
      </div>
      <div v-else>
        <p>현재 저장된 요약 목록이 없습니다.</p>
      </div>
    </div>
  </template>
  
  <script>
  import { getSummaries } from "@/api/sttService";
  
  export default {
    name: "ProfessorReviewView",
    data() {
      return {
        summaries: [],
      };
    },
    async mounted() {
      try {
        this.summaries = await getSummaries();
      } catch (error) {
        console.error("요약 목록 불러오기 실패:", error);
      }
    },
  };
  </script>
  
  <style scoped>
  .review-container {
    max-width: 900px;
    margin: auto;
    padding: 30px;
  }
  .review-item {
    background-color: #f8f9fa;
    border-radius: 12px;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
  }
  </style>