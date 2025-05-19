<template>
  <div class="qna-wrapper">
    <h2 class="title">🎤 실시간 질문 생성 (교수용)</h2>
    <p class="text-muted">"질문"이라는 단어가 감지되면 누적 내용을 기반으로 GPT 질문이 생성됩니다.</p>

    <div class="control-buttons">
      <span class="status">현재 상태: <strong>{{ recognitionStatus }}</strong></span>
    </div>

    <!-- ✅ 렌더링 테스트용 -->
    <p>✅ Prof_AIQnAStu.vue 정상 렌더링됨</p>

    <div class="log-box mt-3">
      <p><strong>🎧 최근 인식된 문장:</strong> {{ latestTranscript }}</p>
      <p v-if="lastTriggeredText"><strong>🧠 최근 질문 트리거:</strong> "{{ lastTriggeredText }}"</p>
    </div>

    <div class="tab-group">
      <button :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</button>
      <!-- popular_summary API가 없으므로 버튼 제거하거나 비활성화 -->
    </div>

    <div v-if="questions.length" class="question-list">
      <div v-for="q in filteredQuestions" :key="q.id" class="question-tile">
        <div class="text">{{ q.text }}</div>
        <div class="meta">👍 {{ q.likes || 0 }} · Anonymous</div>
      </div>
    </div>
    <div v-else class="no-question">아직 질문이 없습니다.</div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";

export default {
  data() {
    return {
      recognitionStatus: '수업 중',
      questions: [],
      latestTranscript: '',
      lastTriggeredText: '',
      transcriptCallback: null,
      pollingInterval: null
    };
  },
  mounted() {
    console.log("🟢 Prof_AIQnAStu.vue mounted");

    this.transcriptCallback = this.handleTranscript;
    recordingManager.subscribeToTranscript(this.transcriptCallback);
    console.log("📡 Subscribed to transcript updates.");

    // 5초마다 질문 생성 요청 → 화면 반영
    this.pollingInterval = setInterval(async () => {
      await this.triggerAndUpdateQuestions();
    }, 5000);
  },
  beforeUnmount() {
    if (this.transcriptCallback) {
      recordingManager.unsubscribeFromTranscript(this.transcriptCallback);
    }
    clearInterval(this.pollingInterval);
  },
  methods: {
    async handleTranscript(transcript) {
      this.latestTranscript = transcript;

      try {
        const lectureId = localStorage.getItem("lecture_id");
        if (!lectureId) return;

        await fetch("https://project2025-backend.onrender.com/vad/upload_text_chunk", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lecture_id: lectureId, text: transcript })
        });
        console.log("📤 텍스트 업로드 완료");
        this.lastTriggeredText = transcript;
      } catch (err) {
        console.error("❌ 텍스트 업로드 실패:", err);
      }
    },

    async triggerAndUpdateQuestions() {
      try {
        const lectureId = localStorage.getItem("lecture_id");
        if (!lectureId) {
          console.warn("⚠️ lecture_id 없음");
          return;
        }

        const res = await fetch("https://project2025-backend.onrender.com/vad/trigger_question_generation", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lecture_id: lectureId })
        });

        const data = await res.json();
        console.log("🧠 질문 생성 응답:", data);

        if (Array.isArray(data.questions)) {
          this.questions = data.questions;
        } else {
          console.warn("❗ 'questions' 배열이 응답에 없음:", data);
        }
      } catch (err) {
        console.error("❌ 질문 생성 요청 실패:", err);
      }
    }
  }
};
</script>
