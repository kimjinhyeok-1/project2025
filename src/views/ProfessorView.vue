<template>
  <div class="dashboard">
    <h2 class="text-gray-800 mb-4">📊 Professor Dashboard</h2>
    <p class="text-muted mb-5">원하시는 메뉴를 선택하세요</p>

    <div class="row g-4">
      <div class="col-md-6">
        <router-link to="/professor/qna" class="card dashboard-card bg-primary text-white text-decoration-none">
          <div class="card-body">
            <h5 class="card-title">❓ Q&A</h5>
            <p class="card-text">학생들의 질문을 확인하고 답변하세요.</p>
          </div>
        </router-link>
      </div>

      <div class="col-md-6">
        <router-link to="/professor/lesson" class="card dashboard-card bg-success text-white text-decoration-none">
          <div class="card-body">
            <h5 class="card-title">🎥 수업하기</h5>
            <p class="card-text">실시간 온라인 강의를 시작하세요.</p>
          </div>
        </router-link>
      </div>

      <div class="col-md-6">
        <router-link to="/professor/review" class="card dashboard-card bg-purple text-white text-decoration-none">
          <div class="card-body">
            <h5 class="card-title">📼 수업 복습</h5>
            <p class="card-text">녹화된 수업을 확인하고 복습하세요.</p>
          </div>
        </router-link>
      </div>

      <div class="col-md-6">
        <router-link to="/professor/assignments" class="card dashboard-card bg-warning text-dark text-decoration-none">
          <div class="card-body">
            <h5 class="card-title">📝 과제</h5>
            <p class="card-text">제출된 과제를 확인하고 피드백하세요.</p>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 20px;
  width: 100%;
}

.dashboard-card {
  transition: all 0.2s ease-in-out;
  border-radius: 12px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
}

.dashboard-card:hover {
  transform: scale(1.02);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
}

.bg-purple {
  background-color: #6f42c1;
}
</style>
