<template>
  <div class="qna-wrapper">
    <h2 class="title">📊 Professor Dashboard</h2>

    <div class="row">
      <div>
        <router-link to="/professor/qna" class="answer-wrapper">
          <div>
            <h5 class="card-title">❓ Q&A</h5>
            <p class="card-text">학생들의 질문을 확인하고 답변하세요.</p>
          </div>
        </router-link>
      </div>

      <div>
        <router-link to="/professor/lesson" class="answer-wrapper">
          <div>
            <h5 class="card-title">🎥 수업하기</h5>
            <p class="card-text">실시간 온라인 강의를 시작하세요.</p>
          </div>
        </router-link>
      </div>

      <div>
        <router-link to="/professor/review" class="answer-wrapper">
          <div>
            <h5 class="card-title">📼 수업 복습</h5>
            <p class="card-text">녹화된 수업을 확인하고 복습하세요.</p>
          </div>
        </router-link>
      </div>

      <div>
        <router-link to="/professor/assignments" class="answer-wrapper">
          <div>
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

.answer-wrapper {
  position: relative;
  width: 950px;
  margin: 1rem auto;
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

.markdown-body {
  font-family: 'Noto Sans', sans-serif;
  line-height: 1.6;
  word-break: break-word;
  margin-bottom: 1rem;
}

.markdown-body pre {
  background-color: #f6f8fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body code {
  background-color: #f6f8fa;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}
</style>