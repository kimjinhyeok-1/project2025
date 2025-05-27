<template>
  <div class="qna-wrapper">
    <!-- 제목 + 버튼 -->
    <div class="title-row">
      <h2 class="title">🎤 수업</h2>
      <button class="btn btn-primary" @click="toggleAudioRecording">
        {{ isRecording ? "🔚 종료" : "🎙️ 수업" }}
      </button>
    </div>

    <!-- 탭 버튼 -->
    <ul class="nav nav-tabs mt-4" style="justify-content: flex-start; width: 950px;">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'summary' }" @click="activeTab = 'summary'">📘 요약</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'ai' }" @click="activeTab = 'ai'; loadPopularQuestions()">🧠 AI 질문</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'student' }" @click="activeTab = 'student'; loadStudentQuestions()">📩 학생 질문</a>
      </li>
    </ul>

    <!-- 📘 요약 -->
    <div v-if="activeTab === 'summary'" class="answer-wrapper right-aligned">
      <h5 class="card-title">📘 수업 요약 결과</h5>
      <div v-if="loadingSummary" class="text-center text-muted">
        요약을 준비하고 있습니다.
      </div>
      <div v-else>
        <div v-for="(summary, idx) in summaries" :key="idx" class="mb-4">
          <div v-if="summary.topic" class="mb-2">
            <h6 class="mb-1">📌 주제</h6>
            <span class="display-6 fw-bold text-primary">{{ summary.topic }}</span>
          </div>
          <div v-html="summary.text"></div>
        </div>
      </div>
    </div>

    <!-- 🧠 AI 질문 -->
    <div v-if="activeTab === 'ai'" class="answer-wrapper">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="card-title">🧠 AI 생성 질문 및 학생 선택 수</h5>
        <button class="btn btn-sm btn-light" @click="loadPopularQuestions()">🔄 새로고침</button>
      </div>
      <div v-if="noQidWarning" class="text-danger text-center">
        ⚠️ q_id가 없어 질문을 불러올 수 없습니다.
      </div>
      <div v-else-if="loadingQuestions" class="text-center text-muted">
        질문 생성중입니다.
      </div>
      <div v-else>
        <div v-for="(q, idx) in placeholderQuestions" :key="idx" class="mb-3">
          <div class="d-flex justify-content-between align-items-center">
            <span>{{ q.text }}</span>
            <span class="likes-badge">선택 수: {{ q.likes }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 📩 학생 질문 -->
    <div v-if="activeTab === 'student'" class="answer-wrapper">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="card-title">📩 학생이 직접 보낸 질문</h5>
        <button class="btn btn-sm btn-light" @click="loadStudentQuestions()">🔄 새로고침</button>
      </div>
      <div v-if="studentQuestions.length === 0" class="text-muted text-center">
        아직 학생 질문이 없습니다.
      </div>
      <div v-else>
        <ul class="list-group">
          <li class="list-group-item" v-for="(q, idx) in studentQuestions" :key="q.id">
            <div class="fw-bold">{{ idx + 1 }}. {{ q.text }}</div>
            <small class="text-muted">🕒 {{ formatDate(q.created_at) }}</small>
          </li>
        </ul>
      </div>
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

.title-row {
  width: 950px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

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
  color: #2c3e50;
}

.card-text {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #34495e;
}

.right-aligned {
  margin-left: auto;
}

/* ✅ 새로 추가된 선택 수 스타일 */
.likes-badge {
  background-color: #008c99;
  color: #ffffff;
  font-size: 1rem;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  font-weight: 600;
  display: inline-block;
}
</style>
