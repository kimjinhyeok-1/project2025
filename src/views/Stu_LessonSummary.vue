<template>
  <div class="review-container text-center mt-5">
    <h2>📚 수업 복습 보기</h2>
    <p class="text-muted">이번 수업 동안 생성된 요약 목록입니다. 원하는 항목을 선택하여 상세 내용을 확인하세요.</p>

    <div v-if="summaries.length" class="mt-5">
      <div
        v-for="(item, index) in summaries"
        :key="index"
        class="review-item mb-4 p-3 d-flex justify-content-between align-items-center"
        @click="goToDetail(item.id)"
        style="cursor: pointer"
      >
        <div class="text-start">
          <p class="mb-1"><strong>🗓 날짜:</strong> {{ formatDate(item.date) }}</p>
          <p class="mb-0"><strong>📘 주차:</strong> {{ item.week }}주차</p>
        </div>
        <div>
          <span class="text-muted">➡️ 클릭하여 상세 보기</span>
        </div>
      </div>
    </div>

    <div v-else class="alert alert-info mt-4">
      현재 저장된 요약 목록이 없습니다.
    </div>
  </div>
</template>

<script>
import { getSummaries } from "@/api/snapshotService";

export default {
  name: "StudentLessonSummary",
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
  methods: {
    formatDate(dateStr) {
      const d = new Date(dateStr);
      return `${d.getMonth() + 1}월 ${d.getDate()}일`;
    },
    goToDetail(id) {
      this.$router.push({ name: "StudentReviewDetail", params: { id } });
    }
  }
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
