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
        <a class="nav-link" :class="{ active: activeTab === 'summary' }" @click="activeTab = 'summary'">
          📘 핵심 키워드
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'ai' }" @click="activeTab = 'ai'; loadPopularQuestions()">
          🧠 이해도 확인 질문
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'student' }" @click="activeTab = 'student'; loadStudentQuestions()">
          📩 학생 질문
        </a>
      </li>
    </ul>

    <!-- 📘 핵심 키워드 -->
    <div v-if="activeTab === 'summary'" class="answer-wrapper right-aligned">
      <h5 class="card-title">📘 오늘의 핵심 키워드</h5>
      <div v-if="loadingSummary" class="text-center text-muted">
        오늘의 핵심 키워드를 준비하고 있습니다.
      </div>
      <div v-else>
        <div v-for="(summary, idx) in summaries" :key="idx" class="mb-4">
          <div v-if="summary.topic" class="mb-2">
            <h6 class="mb-1">📌 키워드 {{ idx + 1 }}</h6>
            <span class="display-6 fw-bold text-primary">{{ summary.topic }}</span>
          </div>
          <div v-html="summary.text"></div>
        </div>
      </div>
    </div>

    <!-- 🧠 이해도 확인 질문 -->
    <div v-if="activeTab === 'ai'" class="answer-wrapper">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="card-title">🧠 이해도 확인 질문 결과</h5>
        <button class="btn btn-sm btn-light" @click="loadPopularQuestions()">🔄 새로고침</button>
      </div>

      <div v-if="generatingQuestions" class="text-muted text-center mb-3">
        🧠 이해도 확인 질문을 생성 중입니다. 잠시만 기다려주세요...
      </div>
      <div v-if="noQidWarning" class="text-danger text-center">
        ⚠️ q_id가 없어 이해도 확인 질문을 불러올 수 없습니다.
      </div>
      <div v-else-if="loadingQuestions" class="text-center text-muted">
        이해도 확인 질문을 불러오는 중입니다.
      </div>
      <div v-else>
        <div v-for="(q, idx) in placeholderQuestions" :key="idx" class="question-row">
          <span class="question-text">{{ q.text }}</span>
          <span class="custom-badge">{{ q.likes }}</span>
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

<script>
import axios from "axios";
import recordingManager from "@/managers/RecordingManager";
import { marked } from "marked";
import { generateLectureSummary, createLecture } from "@/api/snapshotService";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      activeTab: "summary",
      summaries: [],
      isRecording: false,
      latestTranscript: "",
      triggered: false,
      generatingQuestions: false,
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
    formatElapsed(ms) {
      const safe = Math.max(0, Math.round(ms));
      const mm = Math.floor(safe / 60000);
      const ss = Math.floor((safe % 60000) / 1000);
      const cc = Math.floor((safe % 1000) / 10);
      const pad = (n) => String(n).padStart(2, "0");
      return `${pad(mm)}.${pad(ss)}.${pad(cc)}초`;
    },

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

        // 📍 리뷰 생성 시작 시점 기록 추가
        try {
          const __reviewStart = performance.now();
          sessionStorage.setItem("review_timing_start", String(__reviewStart));
          console.log("🕒 리뷰 결과 생성 시작 시점 기록됨");
        } catch (e) {
          console.warn("⚠️ 리뷰 생성 시작시간 기록 실패:", e);
        }

        try {
          const summary = await generateLectureSummary();

          this.summaries = Array.isArray(summary)
            ? summary.map((item) => ({
                text: marked.parse(item.summary || ""),
                topic: item.topic || null
              }))
            : [
                {
                  text: marked.parse(summary.summary || ""),
                  topic: summary.topic || null
                }
              ];

          this.loadingSummary = false;

          const startStr = sessionStorage.getItem("summary_timing_start");
          let elapsedText = "측정 불가";
          if (startStr) {
            const start = Number(startStr);
            const now =
              typeof performance !== "undefined" && typeof performance.now === "function"
                ? performance.now()
                : Date.now();
            elapsedText = this.formatElapsed(now - start);
            sessionStorage.removeItem("summary_timing_start");
          }
          console.log(`✅ 핵심 키워드 생성 완료: 소요 시간(${elapsedText})`);
        } catch (error) {
          this.loadingSummary = false;
          console.error("핵심 키워드 생성 실패:", error);
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
        try {
          const __qStart =
            typeof performance !== "undefined" && typeof performance.now === "function"
              ? performance.now()
              : Date.now();
          sessionStorage.setItem("question_timing_start", String(__qStart));
        } catch (e) {
          console.warn("질문 생성 시작시간 기록 실패:", e);
        }

        this.triggered = true;
        this.generatingQuestions = true;
        try {
          const res = await axios.post("https://project2025-backend.onrender.com/trigger_question_generation");
          const q_id = res.data.q_id;
          this.lastQid = q_id;
          localStorage.setItem("latest_q_id", q_id);
          this.loadPopularQuestions(q_id);
          this.loadStudentQuestions(q_id);
        } catch (error) {
          console.error("질문 생성 API 호출 실패:", error);
        } finally {
          try {
            const startStr = sessionStorage.getItem("question_timing_start");
            let elapsedText = "측정 불가";
            if (startStr) {
              const start = Number(startStr);
              const now =
                typeof performance !== "undefined" && typeof performance.now === "function"
                  ? performance.now()
                  : Date.now();
              elapsedText = this.formatElapsed(now - start);
              sessionStorage.removeItem("question_timing_start");
            }
            console.log(`✅ 이해도 확인 질문 생성 완료: 소요 시간(${elapsedText})`);
          } catch (e) {
            console.warn("질문 생성 시간 로깅 실패:", e);
          }
          this.generatingQuestions = false;
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
        console.error("이해도 확인 질문 조회 실패:", err);
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

.question-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.question-text {
  flex: 1;
  margin-right: 2rem;
  color: #2c3e50;
  font-size: 1rem;
}

.custom-badge {
  background-color: #0a6ebd;
  color: white;
  font-size: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  min-width: 67px;
  text-align: center;
}
</style>
