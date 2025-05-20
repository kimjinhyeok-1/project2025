<template>
  <div class="qna-wrapper">
    <h2 class="title">🎤 질문 생성 감지 페이지</h2>
    <p class="text-muted">RecordingManager에서 질문 생성 요청이 감지되면 여기 출력됩니다.</p>

    <div class="log-box mt-3">
      <p><strong>🎧 최근 인식된 문장:</strong> {{ latestTranscript }}</p>
      <p v-if="triggered"><strong>🧠 POST /vad/trigger_question_generation 호출됨!</strong></p>
    </div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";

export default {
  data() {
    return {
      latestTranscript: "",
      triggered: false,
      transcriptCallback: null
    };
  },
  mounted() {
    console.log("🟢 Prof_AIQnAStu.vue mounted");

    this.transcriptCallback = this.handleTranscript;
    recordingManager.subscribeToTranscript(this.transcriptCallback);
    console.log("📡 Subscribed to transcript updates.");
  },
  beforeUnmount() {
    if (this.transcriptCallback) {
      recordingManager.unsubscribeFromTranscript(this.transcriptCallback);
    }
  },
  methods: {
    async handleTranscript(transcript) {
      this.latestTranscript = transcript;

      if (transcript.includes("질문")) {
        console.log("🧠 POST /vad/trigger_question_generation 호출됨!");
        this.triggered = true;

        // 상태 리셋 (2초 후 다시 false)
        setTimeout(() => {
          this.triggered = false;
        }, 2000);
      }
    }
  }
};
</script>

<style scoped>
.qna-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}
.title {
  font-weight: bold;
}
.log-box {
  background: #f8f9fa;
  padding: 1rem;
  border: 1px dashed #adb5bd;
  border-radius: 0.5rem;
  font-size: 0.9rem;
}
</style>