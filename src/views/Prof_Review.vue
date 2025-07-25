<template>
  <div class="qna-wrapper">
    <h2 class="title">📘 수업 복습 보기</h2>

    <div>
      <!-- lecture_id별로 하나의 카드만 표시 -->
      <div
        v-for="(summary, lectureId) in sortedSummaries"
        :key="lectureId"
        class="answer-wrapper review-item mb-3 px-5 d-flex justify-content-between align-items-center"
        @click="goToDetail(summary.lecture_id)"
        style="cursor: pointer"
      >
        <div>
          <p class="card-text mb-0 fw-bold">{{ formatDate(summary.created_at) }} 수업 요약</p>
        </div>
        <div class="card-text text-end">Click</div>
      </div>

      <div v-if="loading" class="card-text text-muted mt-4 text-center">
        📡 수업 목록을 불러오는 중입니다...
      </div>

      <div v-if="!loading && Object.keys(latestSummaries).length === 0" class="card-text text-danger mt-4 text-center">
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
      groupedSummaries: {},
      latestSummaries: {},
      loading: true,
    };
  },
  computed: {
    sortedSummaries() {
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
      this.$router.push({ name: "ProfessorReviewDetail", params: { id } });
    },
  },
  mounted() {
    this.fetchSummaries();
  },
};
</script>

<style scoped>
/* ===== 기본 레이아웃 ===== */
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: left;
  color: #2c3e50;
  width: 950px;
}

/* ===== 카드 스타일 (과제 항목) ===== */
.answer-wrapper {
  position: relative;
  width: 950px;
  margin: 2rem auto;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.answer-wrapper:hover {
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}

.description-text {
  white-space: pre-line;
}
</style>
