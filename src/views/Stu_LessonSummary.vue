<template>
  <div class="review-container mt-5">
    <h2 class="text-center">📚 수업 복습 보기</h2>
    <p class="text-center text-muted">완료된 수업 요약을 확인할 수 있습니다.</p>

    <div class="mt-5">
      <!-- lecture_id별 그룹 렌더링 -->
      <div v-for="(items, lectureId) in groupedSummaries" :key="lectureId" class="mb-5">
        <h4 class="fw-bold mb-3">🎓 수업 {{ lectureId }}번 요약</h4>

        <div
          v-for="item in items"
          :key="item.created_at"
          class="review-item mb-3 p-3 d-flex justify-content-between align-items-center"
          @click="goToDetail(item.lecture_id)"
          style="cursor: pointer"
        >
          <div>
            <p class="mb-1 fw-bold">📘 {{ formatDate(item.created_at) }}</p>
            <p class="mb-0 text-muted">📝 {{ item.topic }}</p>
          </div>
          <div class="text-muted text-end">➡️ 클릭하여 상세 보기</div>
        </div>
      </div>

      <div v-if="loading" class="text-muted mt-4 text-center">
        📡 수업 목록을 불러오는 중입니다...
      </div>

      <div v-if="!loading && Object.keys(groupedSummaries).length === 0" class="text-danger mt-4 text-center">
        ⚠️ 현재 확인 가능한 수업 요약이 없습니다.
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "StudentLessonSummary",
  data() {
    return {
      groupedSummaries: {},
      loading: true,
    };
  },
  methods: {
    async fetchSummaries() {
      const baseUrl = "https://project2025-backend.onrender.com/snapshots/snapshots/lecture_summaries";
      try {
        const res = await axios.get(baseUrl);
        const data = res.data;

        // 백엔드에서 lecture_id별로 그룹화되어 응답이 오므로 그대로 저장
        this.groupedSummaries = data;
      } catch (err) {
        console.warn("❌ 전체 요약 목록 요청 실패:", err.message);
      } finally {
        this.loading = false;
      }
    },

    formatDate(rawDate) {
      if (!rawDate) return "날짜 미상";
      const date = new Date(rawDate);
      if (isNaN(date.getTime())) return "날짜 오류";
      return `${date.getMonth() + 1}월 ${date.getDate()}일`;
    },

    goToDetail(id) {
      this.$router.push({ name: "StudentReviewDetail", params: { id } });
    },
  },
  mounted() {
    this.fetchSummaries();
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
  transition: all 0.2s ease;
  text-align: left;
}

.review-item:hover {
  background-color: #e9ecef;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
</style>
