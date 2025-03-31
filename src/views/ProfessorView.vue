<template>
  <div class="container mt-5">
    <h2 class="text-center mb-4">📚 Professor Dashboard</h2>
    <p class="text-muted text-center mb-5">원하시는 메뉴를 선택하세요</p>

    <div class="row row-cols-1 row-cols-md-2 g-4">
      <!-- Q&A 카드 -->
      <div class="col">
        <router-link to="/professor/qna" class="text-decoration-none text-dark">
          <div class="card h-100 shadow-sm card-hover bg-light-blue">
            <div class="card-body text-center text-white">
              <h3>❓ Q&A</h3>
              <p class="card-text">학생들의 질문을 확인하고 답변하세요.</p>
            </div>
          </div>
        </router-link>
      </div>

      <!-- 수업하기 카드 -->
      <div class="col">
        <router-link to="/professor/lesson" class="text-decoration-none text-dark">
          <div class="card h-100 shadow-sm card-hover bg-light-green">
            <div class="card-body text-center text-white">
              <h3>🎥 수업하기</h3>
              <p class="card-text">실시간 온라인 강의를 시작하세요.</p>
            </div>
          </div>
        </router-link>
      </div>

      <!-- 수업 복습 카드 -->
      <div class="col">
        <router-link to="/professor-review" class="text-decoration-none text-dark">
          <div class="card h-100 shadow-sm card-hover bg-light-purple">
            <div class="card-body text-center text-white">
              <h3>📼 수업 복습</h3>
              <p class="card-text">녹화된 수업을 확인하고 복습하세요.</p>
            </div>
          </div>
        </router-link>
      </div>

      <!-- 과제 확인 카드 -->
      <div class="col">
        <router-link to="/professor/assignments" class="text-decoration-none text-dark">
          <div class="card h-100 shadow-sm card-hover bg-light-orange">
            <div class="card-body text-center text-white">
              <h3>📝 과제</h3>
              <p class="card-text">제출된 과제를 확인하고 피드백하세요.</p>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProfessorView",
};
</script>

<style scoped>
/* Hover 효과 */
.card-hover {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card-hover:hover {
  transform: scale(1.03);
  box-shadow: 0 0.75rem 1.5rem rgba(0, 0, 0, 0.15);
}

/* 카드별 색상 */
.bg-light-blue {
  background-color: #4e73df;
}
.bg-light-green {
  background-color: #1cc88a;
}
.bg-light-purple {
  background-color: #6f42c1;
}
.bg-light-orange {
  background-color: #f6c23e;
}

/* 텍스트 잘 보이게 */
.card h3,
.card p {
  margin: 0;
}
</style>
