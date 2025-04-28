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
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager"; <!-- ✅ 여기 수정 완료 -->
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
      // 🔥 버튼 상태 강제 반영
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

    // ✅ 진짜 중요: 돌아올 때 음성 인식이 끊겼으면 복구
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
