<template>
  <div class="lecture-container mt-5">
    <h2 class="text-center">🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted text-center">
      녹음 중 키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드에 전송됩니다.
    </p>

    <div class="btn-group d-flex justify-content-center mt-4">
      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>

      <button class="btn btn-warning m-2" @click="testOptions">
        🧪 OPTIONS 테스트
      </button>
    </div>

    <!-- 실시간 요약 결과 -->
    <div v-if="summaryResult && !showFinalSummary" class="alert alert-success mt-4 markdown-body">
      <h5>📘 수업 요약 결과:</h5>
      <div v-html="renderedSummary"></div>
    </div>

    <!-- 수업 종료 후 전체 요약 -->
    <div v-if="showFinalSummary" class="alert alert-primary mt-4 markdown-body">
      <h5>📘 수업 종료 요약:</h5>
      <div v-html="renderedSummary"></div>
    </div>

    <!-- 질문 감지 출력 -->
    <div class="alert alert-info mt-4">
      <p><strong>🎧 최근 인식된 문장:</strong> {{ latestTranscript }}</p>
      <p v-if="triggered"><strong>🧠 질문 생성 요청이 감지되었습니다!</strong></p>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import recordingManager from "@/managers/RecordingManager";
import { marked } from "marked";
import {
  testOptionsRequest,
  generateLectureSummary,
  createLecture
} from "@/api/snapshotService";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isRecording: false,
      summaryResult: null,
      renderedSummary: "",
      latestTranscript: "",
      triggered: false,
      transcriptCallback: null,
      showFinalSummary: false,

      // ✅ 중복 방지용 추가 변수
      isTriggering: false,
      lastTriggeredAt: null
    };
  },
  async mounted() {
    try {
      await createLecture(); // 🔑 lecture_id 생성
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
        this.showFinalSummary = false;
        recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
        try {
          const summary = await generateLectureSummary();
          const markdownText = Array.isArray(summary)
            ? summary.map(item => item.summary || item.text || "").join("\n\n")
            : summary;

          this.summaryResult = markdownText;
          this.renderedSummary = marked.parse(markdownText || "");
          this.showFinalSummary = true;
        } catch (error) {
          if (error.response?.status === 404 || error.response?.status === 400) {
            console.warn("📭 요약 없음 또는 잘못된 요청: 충분한 데이터가 없을 수 있습니다.");
          } else {
            console.error("요약 생성 실패:", error);
          }
        }
      }
    },
    async testOptions() {
      const response = await testOptionsRequest();
      console.log("OPTIONS Response:", response);
    },
    async handleTranscript(text) {
      this.latestTranscript = text;
      const now = Date.now();

      const shouldTrigger =
        (text.includes("질문") || text.includes("?")) &&
        (!this.lastTriggeredAt || now - this.lastTriggeredAt > 5000);

      if (shouldTrigger && !this.isTriggering) {
        this.triggered = true;
        this.isTriggering = true;
        this.lastTriggeredAt = now;

        try {
          await axios.post("https://project2025-backend.onrender.com/vad/trigger_question_generation");
          console.log("🧠 질문 생성 API 호출 완료");
        } catch (error) {
          console.error("질문 생성 API 호출 실패:", error);
        } finally {
          setTimeout(() => {
            this.isTriggering = false;
          }, 2000); // ✅ 최소 2초 대기 후 다시 트리거 가능
        }
      } else {
        this.triggered = false;
      }
    }
  }
};
</script>