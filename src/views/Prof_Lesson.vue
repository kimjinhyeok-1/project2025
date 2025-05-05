<template>
  <div class="lecture-container text-center mt-5">
    <h2>🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted">녹음 중 키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드에 전송됩니다.</p>

    <div class="btn-group mt-4">
      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>

      <button class="btn btn-warning m-2" @click="testOptions">
        🧪 OPTIONS 테스트
      </button>
    </div>

    <div v-if="summaryResult" class="alert alert-success mt-4 text-start" style="white-space: pre-line;">
      <h5>📘 수업 요약 결과:</h5>
      <p>{{ summaryResult }}</p>
    </div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";
import { testOptionsRequest } from "@/api/snapshotService";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isRecording: false,
      lectureId: 1, // TODO: 실제 수업 ID 받아오기
      summaryResult: null,
    };
  },
  methods: {
    async toggleAudioRecording() {
      if (!recordingManager.getState().isRecording) {
        await recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
        this.isRecording = recordingManager.getState().isRecording;

        // ✅ 수업 종료 → 요약 요청
        await this.requestLectureSummary();
      }
      this.isRecording = recordingManager.getState().isRecording;
    },
    async requestLectureSummary() {
      try {
        const response = await fetch(`https://project2025-backend.onrender.com/generate_question_summary?lecture_id=${this.lectureId}`);
        if (!response.ok) throw new Error("요약 요청 실패");

        const data = await response.json();
        this.summaryResult = data.summary;
        console.log("📘 요약 결과:", data.summary);
      } catch (error) {
        console.error("❌ 수업 요약 요청 실패:", error);
        alert("요약 요청에 실패했습니다.");
      }
    },
    async testOptions() {
      await testOptionsRequest();
    },
  },
  mounted() {
    this.isRecording = recordingManager.getState().isRecording;

    recordingManager.subscribe((newState) => {
      this.isRecording = newState;
    });

    recordingManager.reconnectRecognition();
  },
};
</script>

<style scoped>
.lecture-container {
  max-width: 900px;
  margin: auto;
  padding: 30px;
}
</style>
