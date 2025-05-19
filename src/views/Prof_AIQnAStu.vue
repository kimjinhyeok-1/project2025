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
      tab: 'recent',
      questions: [],
      latestTranscript: '',
      lastTriggeredText: '',
      transcriptCallback: null
    };
  },
  computed: {
    filteredQuestions() {
      return [...this.questions].sort((a, b) =>
        new Date(b.created_at) - new Date(a.created_at)
      );
    }
  },
  mounted() {
    console.log("🟢 Prof_AIQnAStu.vue mounted");
    this.fetchQuestions();

    this.transcriptCallback = this.handleTranscript;
    recordingManager.subscribeToTranscript(this.transcriptCallback);
    console.log("📡 Subscribed to transcript updates.");
  },
  beforeUnmount() {
    if (this.transcriptCallback) {
      recordingManager.unsubscribeFromTranscript(this.transcriptCallback);
      console.log("❌ Unsubscribed from transcript updates.");
    }
  },
  watch: {
    tab() {
      this.fetchQuestions();
    }
  },
  methods: {
    async fetchQuestions() {
      try {
        const res = await fetch('https://project2025-backend.onrender.com/vad/questions');
        const data = await res.json();
        console.log("📥 백엔드 질문 목록 응답:", data);

        if (!data.results || !Array.isArray(data.results)) {
          console.warn("❗ 예상치 못한 데이터 구조:", data);
          this.questions = [];
          return;
        }

        this.questions = data.results.map(q => ({
          id: q.id,
          text: q.text,
          created_at: q.created_at,
          likes: q.likes || 0,
          type: q.type || 'ai'
        }));
      } catch (err) {
        console.error("❌ 질문 목록 불러오기 실패:", err);
      }
    },

    async handleTranscript(transcript) {
      console.log("📝 받은 텍스트:", transcript);
      this.latestTranscript = transcript;

      try {
        const uploadRes = await fetch("https://project2025-backend.onrender.com/vad/upload_text_chunk", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: transcript })
        });
        const uploadData = await uploadRes.json();
        console.log("📤 텍스트 업로드 결과:", uploadData);

        if (transcript.includes("질문")) {
          console.log("🧠 '질문' 트리거 감지 → GPT 질문 생성 요청");

          const gptRes = await fetch("https://project2025-backend.onrender.com/vad/trigger_question_generation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
          });

          const gptData = await gptRes.json();
          console.log("📦 GPT 질문 응답:", gptData);

          this.lastTriggeredText = transcript;
          await this.fetchQuestions(); // 갱신
        }
      } catch (err) {
        console.error("❌ 질문 생성 중 오류 발생:", err);
      }
    }
  }
};
</script>
