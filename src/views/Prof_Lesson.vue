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
      <div v-if="loadingSummary" class="text-center text-muted">요약을 준비하고 있습니다.</div>
      <div v-else-if="summaryError" class="text-danger text-center">요약을 불러오는 데 실패했습니다.</div>
      <div v-else>
        <div v-for="(summary, idx) in summaries" :key="idx" class="mb-4">
          <div v-html="summary.text"></div>
        </div>
      </div>
    </div>

    <!-- 🧠 AI 질문 -->
    <div v-if="activeTab === 'ai'" class="answer-wrapper">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="card-title">🧠 질문 선택 결과</h5>
        <button class="btn btn-sm btn-light" @click="loadPopularQuestions()">🔄 새로고침</button>
      </div>
      <div v-if="noQidWarning" class="text-danger text-center">⚠️ q_id가 없어 질문을 불러올 수 없습니다.</div>
      <div v-else-if="loadingQuestions" class="text-center text-muted">질문 생성중입니다.</div>
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
      <div v-if="studentQuestions.length === 0" class="text-muted text-center">아직 학생 질문이 없습니다.</div>
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
      transcriptCallback: null,
      loadingSummary: true,
      summaryError: false,
      loadingQuestions: true,
      noQidWarning: false,
      placeholderQuestions: [],
      lastQid: null,
      studentQuestions: []
    };
  },
  mounted() {
    this.transcriptCallback = this.handleTranscript;
    recordingManager.subscribeToTranscript(this.transcriptCallback);
    this.fetchSummaryFromBackend(); // 처음 summary 탭일 때도 조회
  },
  watch: {
    activeTab(newTab) {
      if (newTab === "summary") {
        this.fetchSummaryFromBackend();
      }
    }
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
        const existing = localStorage.getItem("lecture_id");
        if (!existing) {
          try {
            await createLecture();
          } catch (error) {
            console.error("❌ 강의 세션 생성 실패:", error);
          }
        } else {
          console.log("✅ 기존 lecture_id 사용:", existing);
        }
        recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
        try {
          await generateLectureSummary(); // 생성은 계속 필요
        } catch (error) {
          console.error("요약 생성 실패:", error);
        }
      }
    },
    async fetchSummaryFromBackend() {
      const lectureId = localStorage.getItem("lecture_id");
      if (!lectureId) {
        this.summaryError = true;
        return;
      }
      this.loadingSummary = true;
      this.summaryError = false;
      try {
        const res = await fetch(`https://project2025-backend.onrender.com/snapshots/lecture_key_summary/${1}`);
        if (!res.ok) throw new Error("요약 조회 실패");
        const data = await res.json();
        this.summaries = [{
          text: marked.parse(data.summary || ""),
          topic: null
        }];
      } catch (error) {
        console.error("❌ 요약 조회 실패:", error);
        this.summaryError = true;
      } finally {
        this.loadingSummary = false;
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
