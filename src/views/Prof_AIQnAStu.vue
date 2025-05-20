<template>
  <div class="qna-wrapper">
    <h2 class="title">🎤 실시간 질문 생성 (교수용)</h2>
    <p class="text-muted">"질문"이라는 단어가 감지되면 누적 내용을 기반으로 GPT 질문이 생성됩니다.</p>

    <div class="log-box mt-3">
      <p><strong>🎧 최근 인식된 문장:</strong> {{ latestTranscript }}</p>
      <p v-if="lastTriggeredText"><strong>🧠 최근 질문 트리거:</strong> "{{ lastTriggeredText }}"</p>
    </div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";

export default {
  data() {
    return {
      latestTranscript: '',
      lastTriggeredText: ''
    };
  },
  mounted() {
    recordingManager.onSegment(this.handleSegment);
  },
  methods: {
    async handleSegment(paragraph) {
      this.latestTranscript = paragraph;
      console.log("🧠 인식된 문단:", paragraph);

      await fetch("https://project2025-backend.onrender.com/vad/upload_text_chunk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: paragraph })
      });

      if (paragraph.includes("질문")) {
        console.log("질문 키워드 감지됨");
        await fetch("https://project2025-backend.onrender.com/vad/trigger_question_generation", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({})
        });
        this.lastTriggeredText = paragraph;
      }
    }
  }
};
</script>
