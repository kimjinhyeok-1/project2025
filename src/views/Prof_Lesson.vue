<template>
  <div class="lecture-container mt-5">
    <h2 class="text-center">🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted text-center">
      키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드로 전송됩니다.
    </p>

    <div class="btn-group d-flex justify-content-center mt-4">
      <button class="btn btn-primary m-2" @click="toggleRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>
    </div>

    <div v-if="summaryResult" class="alert alert-success mt-4 markdown-body">
      <h5>📘 수업 요약 결과:</h5>
      <div v-html="renderedSummary"></div>
    </div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";
import { marked } from "marked";
import { generateLectureSummary } from "@/api/snapshotService";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isRecording: false,
      summaryResult: null,
      renderedSummary: ""
    };
  },
  methods: {
    async toggleRecording() {
      if (this.isRecording) {
        recordingManager.stop();
        this.isRecording = false;
      } else {
        recordingManager.setMode("keyword");
        await recordingManager.start();
        this.isRecording = true;
      }
    },

    async testSummary() {
      try {
        const summaryData = await generateLectureSummary();
        this.summaryResult = summaryData.summary_markdown;
        this.renderedSummary = marked.parse(summaryData.summary_markdown);
      } catch (err) {
        console.error("❌ 요약 실패:", err);
      }
    }
  }
};
</script>

<style scoped>
.lecture-container {
  max-width: 800px;
  margin: auto;
  padding: 2rem;
}
</style>
