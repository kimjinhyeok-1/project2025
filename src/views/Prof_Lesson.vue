<template>
  <div class="lecture-container text-center mt-5">
    <h2>🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted">
      녹음 중 키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드에 전송됩니다.
    </p>

    <div class="btn-group mt-4">
      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>

      <button class="btn btn-warning m-2" @click="testOptions">
        🧪 OPTIONS 테스트
      </button>
    </div>

    <div
      v-if="summaryResult"
      class="alert alert-success mt-4 text-start"
      style="white-space: normal;"
    >
      <h5>📘 수업 요약 결과:</h5>
      <div v-html="renderedSummary"></div>
    </div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";
import { testOptionsRequest } from "@/api/snapshotService";
import { marked } from "marked"; // ✅ 마크다운 렌더러 추가

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isRecording: false,
      summaryResult: null,
    };
  },
  computed: {
    // ✅ 마크다운 → HTML로 렌더링
    renderedSummary() {
      return this.summaryResult ? marked.parse(this.summaryResult) : "";
    },
  },
  methods: {
    async toggleAudioRecording() {
      if (!recordingManager.getState().isRecording) {
        await recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
        this.isRecording = recordingManager.getState().isRecording;
        await this.requestLectureSummary(); // 요약 호출
      }
      this.isRecording = recordingManager.getState().isRecording;
    },
    async requestLectureSummary() {
      try {
        const response = await fetch(
          "https://project2025-backend.onrender.com/snapshots/generate_markdown_summary"
        );
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

/* ✅ 마크다운 스타일 조정 */
.alert h3 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #155724;
  margin-top: 1.2rem;
}
.alert ul {
  margin-left: 1.2rem;
  padding-left: 1rem;
}
.alert li {
  margin-bottom: 0.5rem;
}
</style>
