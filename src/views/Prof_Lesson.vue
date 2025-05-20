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
    </div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isRecording: false,
    };
  },
  methods: {
    async toggleAudioRecording() {
      if (this.isRecording) {
        recordingManager.stopRecording();
        this.isRecording = false;
      } else {
        recordingManager.setMode("keyword");
        recordingManager.onKeyword(this.handleKeyword);
        await recordingManager.startRecording();
        this.isRecording = true;
      }
    },
    handleKeyword(transcript) {
      console.log("📌 Prof_Lesson 키워드 감지:", transcript);
    }
  }
};
</script>
