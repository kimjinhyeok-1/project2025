<template>
  <div class="review-container text-center mt-5">
    <h2>📚 수업 복습 보기</h2>
    <p class="text-muted">생성된 수업 요약본을 다운로드할 수 있습니다.</p>

    <!-- ✅ 요약본 목록 -->
    <div v-if="summaries.length" class="mt-5">
      <div
        v-for="(item, index) in summaries"
        :key="index"
        class="review-item mb-4 p-3 d-flex justify-content-between align-items-center"
      >
        <div class="text-start">
          <p class="mb-0">
            📅 <strong>{{ formatDate(item.date) }} ({{ item.week }}주차) 수업 요약본</strong>
          </p>
        </div>
        <div>
          <a
            :href="item.fileUrl"
            download
            class="btn btn-outline-success"
            title="요약본 다운로드"
          >
            📎 첨부파일
          </a>
        </div>
      </div>
    </div>

    <!-- ✅ 요약본 없을 때 -->
    <div v-else class="alert alert-info mt-4">
      현재 저장된 수업 요약본이 없습니다.
    </div>
  </div>
</template>

<script>
export default {
  name: "ProfessorReviewView",
  data() {
    return {
      summaries: [], // 백엔드 연결 전 테스트용 가상 데이터 사용 가능
    };
  },
  async mounted() {
    try {
      // 나중에 실제 API 연결
      // this.summaries = await getSummaries()

      // 🔽 예시 데이터 (프론트 개발용)
      this.summaries = [
        {
          date: '2025-04-24',
          week: 4,
          fileUrl: '/mock/summary_2025_04_24.pdf',
        },
        {
          date: '2025-04-17',
          week: 3,
          fileUrl: '/mock/summary_2025_04_17.pdf',
        }
      ]
    } catch (error) {
      console.error("요약 목록 불러오기 실패:", error);
    }
  },
  methods: {
    formatDate(dateStr) {
      const d = new Date(dateStr);
      const month = d.getMonth() + 1;
      const day = d.getDate();
      return `${month}월 ${day}일`;
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
}
</style>
