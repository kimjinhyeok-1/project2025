<template>
  <div class="qna-wrapper">
    <h2 class="title">🎤 실시간 질문 생성</h2>

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
import recordingManager from '@/managers/RecordingManager';

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
        const base = 'https://project2025-backend.onrender.com/vad';
        const url = this.tab === 'recent' ? `${base}/questions` : `${base}/questions/popular_summary`;
        const res = await fetch(url);
        const data = await res.json();
        this.questions = this.tab === 'recent'
          ? data.results
          : data.results.map(q => ({
              text: `${q.text} (${q.unknown_percent}%)`,
              created_at: new Date()
            }));
      } catch (err) {
        console.error('❌ 질문 목록 불러오기 실패:', err);
      }
    },
    startRecognition() {
      recordingManager.setMode('segment');
      recordingManager.startRecording();
      recordingManager.onSegment(this.handleSegment);
      this.recognitionStatus = '음성 인식 중';
    },
    stopRecognition() {
      recordingManager.stopRecording();
      this.recognitionStatus = '정지됨';
    },
    async handleSegment(transcript) {
      this.latestTranscript = transcript;
      console.log('🎙️ 인식된 문장:', transcript);

      try {
        const uploadRes = await fetch('https://project2025-backend.onrender.com/vad/upload_text_chunk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: transcript })
        });
        const uploadData = await uploadRes.json();
        console.log('✅ 텍스트 업로드:', uploadData.message);

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
      } catch (err) {
        console.error('❌ 질문 생성 처리 실패:', err);
      }
    }
  }
}
</script>

<style scoped>
/* 스타일 원본 그대로 유지 */
.qna-wrapper { max-width: 800px; margin: 0 auto; padding: 2rem; }
.title { font-weight: bold; }
.control-buttons { margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem; }
.start-btn, .stop-btn {
  padding: 0.5rem 1rem; border: none; border-radius: 0.375rem;
  color: white; cursor: pointer;
}
.start-btn { background-color: #0d6efd; }
.stop-btn { background-color: #dc3545; }
.status { font-size: 0.9rem; }

.tab-group { display: flex; gap: 1rem; margin: 1rem 0; }
.tab-group button {
  padding: 0.5rem 1rem; border: none;
  background: #e9ecef; border-radius: 0.375rem; cursor: pointer;
}
.tab-group .active { background-color: #0d6efd; color: white; }

.question-list { margin-top: 1rem; }
.question-tile {
  background: white; border: 1px solid #dee2e6;
  border-radius: 0.5rem; padding: 1rem; margin-bottom: 0.75rem;
}
.question-tile .meta {
  font-size: 0.85rem; color: #6c757d; margin-top: 0.5rem;
}
.no-question { color: #6c757d; text-align: center; margin-top: 2rem; }

.log-box {
  background: #f8f9fa;
  padding: 1rem;
  border: 1px dashed #adb5bd;
  border-radius: 0.5rem;
  font-size: 0.9rem;
}
</style>
