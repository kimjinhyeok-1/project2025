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

    <div v-if="summaryResult" class="alert alert-success mt-4 markdown-body">
      <h5>📘 수업 요약 결과:</h5>
      <div v-html="renderedSummary"></div>
    </div>

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
import { testOptionsRequest, generateLectureSummary } from "@/api/snapshotService";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isRecording: false,
      summaryResult: null,
      renderedSummary: "",
      latestTranscript: "",
      triggered: false,
      transcriptCallback: null
    };
  },
  mounted() {
    this.transcriptCallback = this.handleTranscript;
    recordingManager.subscribeToTranscript(this.transcriptCallback);
  },
  beforeUnmount() {
    if (this.transcriptCallback) {
      recordingManager.unsubscribeFromTranscript(this.transcriptCallback);
    }
  },
  methods: {
    toggleAudioRecording() {
      this.isRecording = !this.isRecording;
      if (this.isRecording) {
        recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
      }
    },
    async testOptions() {
      const response = await testOptionsRequest();
      console.log("OPTIONS Response:", response);
    },
    async handleTranscript(text) {
      this.latestTranscript = text;

      const lectureId = localStorage.getItem("lecture_id");
      const token = localStorage.getItem("access_token");

      if (!lectureId || !token) {
        console.error("❌ lecture_id 또는 access_token 없음. 먼저 로그인하고 수업을 시작하세요.");
        return;
      }

      if (text.includes("질문") || text.includes("?")) {
        this.triggered = true;
        try {
          await axios.post(
            "https://project2025-backend.onrender.com/vad/trigger_question_generation",
            { lecture_id: lectureId },
            {
              headers: {
                Authorization: `Bearer ${token}`
              },
              withCredentials: true
            }
          );
        } catch (error) {
          console.error("질문 생성 API 호출 실패:", error);
        }
      } else {
        this.triggered = false;
      }

      try {
        const summary = await generateLectureSummary(text, lectureId);
        this.summaryResult = summary;
        this.renderedSummary = marked.parse(summary || "");
      } catch (error) {
        console.error("요약 생성 실패:", error);
      }
    }
  }
};
</script>
