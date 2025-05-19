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
      const validLectureIds = [2, 3, 4];

      for (let id of validLectureIds) {
        try {
          const res = await axios.get(`${baseUrl}?lecture_id=${id}`);
          const summaries = res.data;

          if (Array.isArray(summaries) && summaries.length > 0) {
            const topic = summaries[0].topic;
            const date = this.convertToDate(summaries[0].created_at);

            results.push({
              lecture_id: id,
              topic,
              dateLabel: date
                ? `${date.getMonth() + 1}월 ${date.getDate()}일 수업 요약본`
                : `날짜 미상 수업 요약본`,
            });
          }
        } catch (err) {
          console.warn(`❌ 요청 실패: lecture_id=${id}`, err.message);
        }
      }

      this.summaryList = results.sort((a, b) => b.lecture_id - a.lecture_id);
      this.loading = false;
    },

    convertToDate(rawDate) {
      if (!rawDate) return null;
      const parsed = new Date(rawDate);
      if (isNaN(parsed.getTime())) return null;
      return parsed; // ✅ KST 보정 제거
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
  transition: all 0.2s ease; /* ✅ 배경 + 그림자 + 이동 효과 포함 */
  text-align: left; /* ✅ 왼쪽 정렬 유지 */
}

.review-item:hover {
  background-color: #e9ecef;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* ✅ 그림자 강조 */
  transform: translateY(-2px); /* ✅ 살짝 떠오르는 효과 */
}
</style>

