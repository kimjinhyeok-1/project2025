<template>
  <div class="review-container text-center mt-5">
    <h2>📚 수업 복습 보기</h2>
    <p class="text-muted">완료된 수업 요약을 확인할 수 있습니다.</p>

    <div class="mt-5">
      <div
        v-for="item in summaryList"
        :key="item.lecture_id"
        class="review-item mb-4 p-3 d-flex justify-content-between align-items-center"
        @click="goToDetail(item.lecture_id)"
        style="cursor: pointer"
      >
        <div class="text-start">
          <p class="mb-1"><strong>📘 Lecture ID:</strong> {{ item.lecture_id }}</p>
          <p class="mb-0"><strong>📝 Topic:</strong> {{ item.topic }}</p>
        </div>
        <div>
          <span class="text-muted">➡️ 클릭하여 상세 보기</span>
        </div>
      </div>

      <div v-if="loading" class="text-muted mt-4">📡 수업 목록을 불러오는 중입니다...</div>
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
      let currentId = 1;
      let consecutiveFails = 0;
      const maxConsecutiveFails = 10;

      while (consecutiveFails < maxConsecutiveFails) {
        try {
          const res = await axios.get(`${baseUrl}?lecture_id=${currentId}`);
          if (res.data && res.data.length > 0) {
            results.push({
              lecture_id: currentId,
              topic: res.data[0].topic,
            });
            consecutiveFails = 0; // 성공하면 실패 카운터 리셋
          } else {
            consecutiveFails++;
          }
        } catch (err) {
          consecutiveFails++;
        }

        currentId++;
      }

      this.summaryList = results;
      this.loading = false;
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
