<template>
  <div class="qna-wrapper">
    <div class="title-bar mb-4" style="width: 950px;">
      <h2 class="title">📊 Professor Dashboard</h2>
    </div>

    <div class="dashboard-grid">
      <router-link to="/professor/qna" class="dashboard-card">
        <div class="card-inner">
          <h5 class="card-title">❓ Q&A</h5>
          <p class="card-text">학생들의 질문을 확인하고 답변하세요.</p>
        </div>
      </router-link>

      <router-link to="/professor/lesson" class="dashboard-card">
        <div class="card-inner">
          <h5 class="card-title">🎥 수업하기</h5>
          <p class="card-text">실시간 온라인 강의를 시작하세요.</p>
        </div>
      </router-link>

      <router-link to="/professor/review" class="dashboard-card">
        <div class="card-inner">
          <h5 class="card-title">📼 수업 복습</h5>
          <p class="card-text">녹화된 수업을 확인하고 복습하세요.</p>
        </div>
      </router-link>

      <router-link to="/professor/assignments" class="dashboard-card">
        <div class="card-inner">
          <h5 class="card-title">📝 과제</h5>
          <p class="card-text">제출된 과제를 확인하고 피드백하세요.</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  text-align: left;
  color: #2c3e50;
}

/* ✅ 카드 2열로 구성하는 Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 20px;
  width: 950px;
}

/* ✅ 카드 스타일 */
.dashboard-card {
  display: block;
  background: linear-gradient(145deg, #f9fafb, #ffffff);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  text-decoration: none;
  color: #212529;
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
  background-color: #f1f3f5;
}

.card-inner {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 0.8rem;
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}
</style>
