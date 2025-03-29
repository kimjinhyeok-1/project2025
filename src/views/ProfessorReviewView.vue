<template>
    <div class="review-container text-center mt-5">
      <h2>📚 수업 복습 보기</h2>
      <p class="text-muted">이번 수업 동안 인식된 키워드 문장과 그 시점의 화면 캡처입니다.</p>
  
      <div v-if="reviewItems.length" class="mt-5">
        <div
          v-for="(item, index) in reviewItems"
          :key="index"
          class="review-item mb-5"
        >
          <img :src="item.screenshot" class="screenshot mb-2" />
          <p><strong>⏱ 타임스탬프:</strong> {{ item.timestamp }}</p>
          <p><strong>🎙 인식된 문장:</strong> "{{ item.transcript }}"</p>
          <hr />
        </div>
      </div>
      <div v-else>
        <p>녹음 세션 중 저장된 스크린샷이 아직 없습니다.</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "ProfessorReviewView",
    data() {
      return {
        reviewItems: [],
      };
    },
    mounted() {
      // 수업 중 저장된 screenshotLog를 불러오기
      const raw = sessionStorage.getItem("screenshotLog");
      if (raw) {
        this.reviewItems = JSON.parse(raw);
      }
    },
  };
  </script>
  
  <style scoped>
  .review-container {
    max-width: 900px;
    margin: auto;
    padding: 30px;
  }
  .screenshot {
    max-width: 100%;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  .review-item {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
  }
  </style>
  