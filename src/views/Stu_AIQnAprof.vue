<template>
  <div class="qna-wrapper">
    <h2 class="title">🎤 실시간 질문 생성 (교수용)</h2>
    <p class="text-muted">"질문"이라는 단어가 감지되면 누적 내용을 기반으로 GPT 질문이 생성됩니다.</p>

    <div class="control-buttons">
      <button class="start-btn" @click="startRecognition">🎙️ 수업 시작</button>
      <button class="stop-btn" @click="stopRecognition">🛑 수업 종료</button>
      <span class="status">현재 상태: <strong>{{ recognitionStatus }}</strong></span>
    </div>

    <div class="log-box mt-3">
      <p><strong>🎧 최근 인식된 문장:</strong> {{ latestTranscript }}</p>
      <p v-if="lastTriggeredText"><strong>🧠 최근 질문 트리거:</strong> "{{ lastTriggeredText }}"</p>
    </div>

    <div class="tab-group">
      <button :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</button>
      <button :class="{ active: tab === 'popular' }" @click="tab = 'popular'">Popular</button>
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
      recognitionStatus: '정지됨',
      tab: 'recent',
      questions: [],
      latestTranscript: '',
      lastTriggeredText: ''
    }
  },
  computed: {
    filteredQuestions() {
      return [...this.questions].sort((a, b) =>
        this.tab === 'popular' ? b.likes - a.likes : new Date(b.created_at) - new Date(a.created_at)
      );
    }
  },
  mounted() {
    this.fetchQuestions();
  },
  watch: {
    tab() {
      this.fetchQuestions();
    }
  },
  methods: {
    async fetchQuestions() {
      try {
        const url = this.tab === 'recent'
          ? 'https://project2025-backend.onrender.com/vad/questions'
          : 'https://project2025-backend.onrender.com/vad/questions/popular_summary';
        const res = await fetch(url);
        const data = await res.json();
        this.questions = this.tab === 'recent' ? data.results : data.results.map(q => ({
          text: `${q.text} (${q.unknown_percent}%)`,
          created_at: new Date()
        }));
      } catch (err) {
        console.error('❌ 질문 목록 불러오기 실패:', err);
      }
    },
    async startRecognition() {
      recordingManager.setMode("segment");
      await recordingManager.start();
      this.recognitionStatus = '음성 인식 중';

      recordingManager.onSegment(async (transcript) => {
        this.latestTranscript = transcript;
        console.log('🎙️ 인식된 문장:', transcript);

        // 텍스트 업로드
        await fetch('https://project2025-backend.onrender.com/vad/upload_text_chunk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: transcript })
        });

        if (transcript.includes('질문')) {
          console.log('🧠 "질문" 트리거 감지 → GPT 질문 생성 요청');
          const gptRes = await fetch('https://project2025-backend.onrender.com/vad/trigger_question_generation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
          });
          const gptData = await gptRes.json();
          console.log('📦 GPT 질문 응답:', gptData.questions);
          this.lastTriggeredText = transcript;
          await this.fetchQuestions();
        }
      });
    },
    stopRecognition() {
      recordingManager.stop();
      this.recognitionStatus = '정지됨';
    }
  }
}
</script>

<style scoped>
/* ... 기존 스타일 그대로 유지 ... */
</style>
