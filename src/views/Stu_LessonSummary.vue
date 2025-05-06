<template>
  <div class="review-container text-center mt-5">
    <h2>📚 수업 복습 보기</h2>
    <p class="text-muted">완료된 수업 요약을 확인할 수 있습니다.</p>

    <div class="mt-5">
      <div
        class="review-item mb-4 p-3 d-flex justify-content-between align-items-center"
        @click="goToDetail"
        style="cursor: pointer"
      >
        <div class="text-start">
          <p class="mb-1"><strong>🗓 날짜:</strong> 2025-05-05</p>
          <p class="mb-0"><strong>📘 주차:</strong> 6주차</p>
        </div>
        <div>
          <span class="text-muted">➡️ 클릭하여 상세 보기</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "StudentLessonSummary",
  methods: {
    goToDetail() {
      this.$router.push({ name: "StudentReviewDetail", params: { id: 1 } }); // 강의 ID 고정
    },
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
  transition: background-color 0.2s ease;
}
.review-item:hover {
  background-color: #e9ecef;
}
</style>
