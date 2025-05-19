<template>
  <div class="review-container text-center mt-5">
    <h2>📚 수업 복습 보기</h2>
    <p class="text-muted">완료된 수업 요약을 확인할 수 있습니다.</p>

    <div class="mt-5">
      <!-- 수업 리스트 -->
      <div
        v-for="item in summaryList"
        :key="item.lecture_id"
        class="review-item mb-4 p-3 d-flex justify-content-between align-items-center"
        @click="goToDetail(item.lecture_id)"
        style="cursor: pointer"
      >
        <div class="text-start">
          <p class="mb-1 fw-bold">📘 {{ item.dateLabel }}</p>
          <p class="mb-0 text-muted">📝 {{ item.topic }}</p>
        </div>
        <div>
          <span class="text-muted">➡️ 클릭하여 상세 보기</span>
        </div>
      </div>

      <!-- 로딩 중 -->
      <div v-if="loading" class="text-muted mt-4">
        📡 수업 목록을 불러오는 중입니다...
      </div>

      <!-- 요약 없음 -->
      <div v-if="!loading && summaryList.length === 0" class="text-danger mt-4">
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
      summaryList: [],
      loading: true,
    };
  },
  methods: {
    async fetchSummaries() {
      const baseUrl = "https://project2025-backend.onrender.com/snapshots/lecture_summary";
      const results = [];
      const maxLectureId = 30;

      for (let id = 1; id <= maxLectureId; id++) {
        try {
          const res = await axios.get(`${baseUrl}?lecture_id=${id}`);
          if (res.data && res.data.length > 0) {
            const item = res.data[0];
            const date = this.convertToKoreanDate(item.created_at);
            results.push({
              lecture_id: id,
              topic: item.topic,
              dateLabel: `${date.getMonth() + 1}월 ${date.getDate()}일 수업 요약본`,
            });
          }
        } catch (err) {
          // 요약 없는 강의는 무시
        }
      }

      // 최신 수업이 위로 오도록 정렬
      this.summaryList = results.sort((a, b) => b.lecture_id - a.lecture_id);
      this.loading = false;
    },

    convertToKoreanDate(utcDateStr) {
      const utc = new Date(utcDateStr);
      const koreaTime = new Date(utc.getTime() + 8 * 60 * 60 * 1000);
      return koreaTime;
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
  transition: background-color 0.2s ease;
}
.review-item:hover {
  background-color: #e9ecef;
}
</style>
