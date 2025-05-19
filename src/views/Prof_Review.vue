<template>
  <div class="review-container mt-5">
    <h2 class="text-center">📚 수업 복습 보기</h2>
    <p class="text-center text-muted">완료된 수업 요약을 확인할 수 있습니다.</p>

    <div class="mt-5">
      <div
        v-for="item in summaryList"
        :key="item.lecture_id"
        class="review-item mb-4 p-3 d-flex justify-content-between align-items-center"
        @click="goToDetail(item.lecture_id)"
        style="cursor: pointer"
      >
        <!-- 왼쪽 -->
        <div>
          <p class="mb-1 fw-bold">📘 {{ item.dateLabel }}</p>
          <p class="mb-0 text-muted">📝 {{ item.topic }}</p>
        </div>

        <!-- 오른쪽 -->
        <div class="text-muted text-end">➡️ 클릭하여 상세 보기</div>
      </div>

      <div v-if="loading" class="text-muted mt-4 text-center">
        📡 수업 목록을 불러오는 중입니다...
      </div>

      <div v-if="!loading && summaryList.length === 0" class="text-danger mt-4 text-center">
        ⚠️ 현재 확인 가능한 수업 요약이 없습니다.
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ProfessorReviewView",
  data() {
    return {
      summaryList: [],
      loading: true,
    };
  },
  methods: {
    async fetchSummaries() {
      const baseUrl = "https://project2025-backend.onrender.com/snapshots/lecture_summaries"; // ✅ 변경 완료
      try {
        const res = await axios.get(baseUrl);
        const data = res.data;

        this.summaryList = data
          .map((item) => {
            const date = this.convertToDate(item.created_at);
            return {
              lecture_id: item.lecture_id,
              topic: item.topic,
              dateLabel: date
                ? `${date.getMonth() + 1}월 ${date.getDate()}일 수업 요약본`
                : `날짜 미상 수업 요약본`,
            };
          })
          .sort((a, b) => b.lecture_id - a.lecture_id);
      } catch (err) {
        console.warn("❌ 전체 요약 목록 요청 실패:", err.message);
      } finally {
        this.loading = false;
      }
    },

    convertToDate(rawDate) {
      if (!rawDate) return null;
      const parsed = new Date(rawDate);
      if (isNaN(parsed.getTime())) return null;
      return parsed;
    },

    goToDetail(id) {
      this.$router.push({ name: "ProfessorReviewDetail", params: { id } });
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
