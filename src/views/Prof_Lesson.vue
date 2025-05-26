<template>
  <div class="qna-wrapper">
    <!-- 제목 + 버튼 -->
    <div class="title-row">
      <h2 class="title">🎤 수업 녹화 & 음성 인식</h2>
      <button class="btn btn-primary" @click="toggleAudioRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>
    </div>

    <!-- 실시간 요약 결과 -->
    <div class="answer-wrapper right-aligned">
      <div class="card-header card-text">
        📘 수업 요약 결과
      </div>
      <div class="card-body card-text">
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
    </div>

    <!-- AI 질문 및 좋아요 -->
    <div class="answer-wrapper">
      <div class="card-header card-text">
        <span>🧠 AI 생성 질문 및 학생 선택 수</span>
        <button class="btn btn-sm btn-light" @click="loadPopularQuestions()">🔄 질문 불러오기</button>
      </div>
      <div class="card-body card-text">
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
              <span class="badge bg-info">선택 수: {{ q.likes }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 학생 직접 질문 출력 -->
    <div class="answer-wrapper">
      <div class="card-header card-text">
        <span>📩 학생이 직접 보낸 질문</span>
        <button class="btn btn-sm btn-light" @click="loadStudentQuestions()">🔄 새로고침</button>
      </div>
      <div class="card-body card-text">
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
  </div>
</template>

<script>
import axios from "axios";
import recordingManager from "@/managers/RecordingManager";
import { marked } from "marked";
import { generateLectureSummary, createLecture } from "@/api/snapshotService";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      summaries: [],
      isRecording: false,
      latestTranscript: "",
      triggered: false,
      transcriptCallback: null,
      loadingSummary: true,
      loadingQuestions: true,
      noQidWarning: false,
      placeholderQuestions: [],
      lastQid: null,
      studentQuestions: []
    };
  },
  async mounted() {
    try {
      await createLecture();
    } catch (err) {
      console.error("강의 세션 생성 실패:", err);
    }
    this.transcriptCallback = this.handleTranscript;
    recordingManager.subscribeToTranscript(this.transcriptCallback);
  },
  beforeUnmount() {
    if (this.transcriptCallback) {
      recordingManager.unsubscribeFromTranscript(this.transcriptCallback);
    }
  },
  methods: {
    formatDate(datetimeStr) {
      const date = new Date(datetimeStr);
      return date.toLocaleString("ko-KR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      });
    },
    async toggleAudioRecording() {
      this.isRecording = !this.isRecording;
      if (this.isRecording) {
        this.loadingSummary = true;
        recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
        try {
          const summary = await generateLectureSummary();
          this.summaries = Array.isArray(summary)
            ? summary.map(item => ({
                text: marked.parse(item.summary || ""),
                topic: item.topic || null
              }))
            : [ {
                text: marked.parse(summary.summary || ""),
                topic: summary.topic || null
              }];
          this.loadingSummary = false;
        } catch (error) {
          this.loadingSummary = false;
          console.error("요약 생성 실패:", error);
        }
      }
    },
    async handleTranscript(text) {
      this.latestTranscript = text;
      try {
        await axios.post("https://project2025-backend.onrender.com/upload_text_chunk", { text });
      } catch (error) {
        console.error("❌ 텍스트 업로드 실패:", error);
      }

      if (text.includes("질문")) {
        this.triggered = true;
        try {
          const res = await axios.post("https://project2025-backend.onrender.com/trigger_question_generation");
          const q_id = res.data.q_id;
          this.lastQid = q_id;
          localStorage.setItem("latest_q_id", q_id);
          this.loadPopularQuestions(q_id);
          this.loadStudentQuestions(q_id);
        } catch (error) {
          console.error("질문 생성 API 호출 실패:", error);
        }
      } else {
        this.triggered = false;
      }
    },
    async loadPopularQuestions(q_id = null) {
      const id = q_id || this.lastQid || localStorage.getItem("latest_q_id");
      if (!id) {
        this.noQidWarning = true;
        this.loadingQuestions = false;
        return;
      }

      this.noQidWarning = false;
      this.loadingQuestions = true;
      try {
        const res = await fetch(`https://project2025-backend.onrender.com/questions/popular_likes?q_id=${id}`);
        const data = await res.json();
        if (Array.isArray(data.results)) {
          this.placeholderQuestions = data.results;
        }
      } catch (err) {
        console.error("인기 질문 조회 실패:", err);
      } finally {
        this.loadingQuestions = false;
      }
    },
    async loadStudentQuestions(q_id = null) {
      const id = q_id || this.lastQid || localStorage.getItem("latest_q_id");
      if (!id) {
        console.warn("q_id 없음: 학생 질문을 불러올 수 없습니다.");
        return;
      }

      try {
        const res = await fetch(`https://project2025-backend.onrender.com/student_questions?q_id=${id}`);
        const data = await res.json();
        if (Array.isArray(data.results)) {
          this.studentQuestions = data.results;
          console.log("✅ 학생 직접 질문 수신:", data.results.length);
        } else {
          console.warn("❓ 학생 질문 응답 형식 이상:", data);
        }
      } catch (err) {
        console.error("❌ 학생 질문 불러오기 실패:", err);
      }
    }
  }
};
</script>

<style scoped>
.markdown-body {
  white-space: pre-wrap;
}

/* ===== 기본 레이아웃 ===== */
.qna-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5rem;
}

/* 제목 + 버튼 한 줄로 */
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

/* ===== 카드 스타일 ===== */
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

.right-aligned {
  margin-left: auto;
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
