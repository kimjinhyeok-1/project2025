<template>
  <div class="review-container mt-5">
    <h2 class="text-center">📚 수업 복습 보기</h2>
    <p class="text-center text-muted">완료된 수업 요약을 확인할 수 있습니다.</p>

    <div class="mt-5">
      <!-- lecture_id별로 하나의 카드만 표시 -->
      <div
        v-for="(summary, lectureId) in sortedSummaries"
        :key="lectureId"
        class="review-item mb-3 p-3 d-flex justify-content-between align-items-center"
        @click="goToDetail(summary.lecture_id)"
        style="cursor: pointer"
      >
        <div>
          <p class="mb-0 fw-bold">📘 {{ formatDate(summary.created_at) }} 수업 요약본</p>
        </div>
        <div class="text-muted text-end">➡️ 클릭하여 상세 보기</div>
      </div>

      <div v-if="loading" class="text-muted mt-4 text-center">
        📡 수업 목록을 불러오는 중입니다...
      </div>

      <div v-if="!loading && Object.keys(latestSummaries).length === 0" class="text-danger mt-4 text-center">
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
      groupedSummaries: {},     // 전체 수업 요약
      latestSummaries: {},      // lecture_id별 최신 하나만 저장
      loading: true,
    };
  },
  computed: {
    sortedSummaries() {
      // lecture_id 숫자 내림차순 정렬
      return Object.keys(this.latestSummaries)
        .sort((a, b) => Number(b) - Number(a))
        .reduce((acc, key) => {
          acc[key] = this.latestSummaries[key];
          return acc;
        }, {});
    },
  },
  methods: {
    async fetchSummaries() {
      const baseUrl = "https://project2025-backend.onrender.com/snapshots/snapshots/lecture_summaries";
      try {
        const res = await axios.get(baseUrl);
        const data = res.data;
        this.groupedSummaries = data;

        // 각 lecture_id 그룹 내 가장 최신 created_at 항목만 추출
        const latest = {};
        for (const [lectureId, items] of Object.entries(data)) {
          if (items.length > 0) {
            const sortedItems = items.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            latest[lectureId] = sortedItems[0];
          }
        }
        this.latestSummaries = latest;
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
