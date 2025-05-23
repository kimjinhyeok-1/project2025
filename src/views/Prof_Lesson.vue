<template>
  <div class="lecture-container mt-5 mx-auto px-4" style="max-width: 960px;">
    <h2 class="text-center">🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted text-center">
      녹음 중 키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드에 전송됩니다.
    </p>

    <div class="btn-group d-flex justify-content-center mt-4">
      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>
    </div>

    <!-- 실시간 요약 결과 -->
    <div class="card mt-4">
      <div class="card-header bg-primary text-white">
        📘 수업 요약 결과
      </div>
      <div class="card-body">
        <div v-if="loadingSummary" class="text-center text-muted">
          요약을 준비하고 있습니다.
        </div>
        <div v-else>
          <div v-for="(summary, idx) in summaries" :key="idx" class="mb-4">
            <div v-if="summary.topic" class="mb-2">
              <h6 class="mb-1">📌 주제</h6>
              <span class="badge bg-secondary">{{ summary.topic }}</span>
            </div>
            <div v-html="summary.text"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 질문 감지 출력 -->
    <div class="alert alert-info mt-4">
      <p><strong>🎧 최근 인식된 문장:</strong> {{ latestTranscript }}</p>
      <p v-if="triggered"><strong>🧠 질문 생성 요청이 감지되었습니다!</strong></p>
    </div>

    <!-- 교수용 질문 확인 UI -->
    <div class="card mt-5">
      <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
        <span>🧠 AI 생성 질문 및 학생 선택 수</span>
        <button class="btn btn-sm btn-light" @click="loadPopularQuestions">🔄 질문 불러오기</button>
      </div>
      <div class="card-body">
        <div v-if="loadingQuestions" class="text-center text-muted">
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
      placeholderQuestions: []
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
            : [{
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
        await axios.post("https://project2025-backend.onrender.com/upload_text_chunk", {
          text
        });
      } catch (error) {
        console.error("❌ 텍스트 업로드 실패:", error);
      }

      if (text.includes("질문") || text.includes("?") || text.includes("확인")) {
        this.triggered = true;
        try {
          const res = await axios.post("https://project2025-backend.onrender.com/trigger_question_generation");
          const q_id = res.data.q_id;
          console.log("🧠 질문 생성 API 호출 완료 - q_id:", q_id);
          this.loadPopularQuestions(q_id);
        } catch (error) {
          console.error("질문 생성 API 호출 실패:", error);
        }
      } else {
        this.triggered = false;
      }
    },
    async loadPopularQuestions(q_id = null) {
      this.loadingQuestions = true;
      try {
        if (!q_id) {
          const res = await fetch("https://project2025-backend.onrender.com/questions/latest");
          const data = await res.json();
          q_id = data?.q_id;
        }

        if (!q_id) throw new Error("q_id가 없습니다.");

        const res = await fetch(`https://project2025-backend.onrender.com/questions/popular_likes?q_id=${q_id}`);
        const data = await res.json();
        if (Array.isArray(data.results)) {
          this.placeholderQuestions = data.results;
        }
      } catch (err) {
        console.error("인기 질문 조회 실패:", err);
      } finally {
        this.loadingQuestions = false;
      }
    }
  }
};
</script>

<style scoped>
.markdown-body {
  white-space: pre-wrap;
}
</style>
