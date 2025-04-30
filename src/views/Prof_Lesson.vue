<template>
  <div class="lecture-container text-center mt-5">
    <h2>🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted">녹음 중 AI가 중요하다고 판단한 문장이 나오면 자동으로 스크린샷을 캡처하고 백엔드에 저장합니다.</p>

    <div class="btn-group mt-4">
      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>

      <button class="btn btn-warning m-2" @click="testOptions">
        🧪 OPTIONS 테스트
      </button>
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
    };
  },
  methods: {
    async toggleAudioRecording() {
      if (!recordingManager.getState().isRecording) {
        await recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
      }
      this.isRecording = recordingManager.getState().isRecording;
    },
    async testOptions() {
      await testOptionsRequest();
    }
  },
  mounted() {
    this.isRecording = recordingManager.getState().isRecording;

    recordingManager.subscribe((newState) => {
      this.isRecording = newState;
    });

    recordingManager.reconnectRecognition();
  }
};
</script>

<style scoped>
.lecture-container {
  max-width: 900px;
  margin: auto;
  padding: 30px;
}
</style>
