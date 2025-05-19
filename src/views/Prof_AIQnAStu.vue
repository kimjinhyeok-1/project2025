<template>
  <div class="px-7 py-8">
    <h3 class="fw-bold mb-2">🎤 실시간 질문 생성 (교수용)</h3>
    <p class="text-muted mb-4">"질문"이라는 단어가 감지되면 이전까지의 내용을 기반으로 GPT 질문이 생성됩니다.</p>

    <div class="d-flex align-items-center justify-content-between bg-light border rounded p-3 mb-4">
      <span class="fw-semibold">현재 상태: {{ recognitionStatus }}</span>
      <small class="text-muted">누적 문장 수: {{ sentenceCount }}</small>
    </div>

    <div class="d-flex gap-2 mb-4">
      <button class="btn btn-success" @click="startRecognition">🎙️ 수업 시작</button>
      <button class="btn btn-danger" @click="stopRecognition">🛑 수업 종료</button>
    </div>

    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: tab === 'popular' }" @click="tab = 'popular'">Popular</a>
      </li>
    </ul>

    <div v-if="filteredQuestions.length">
      <div
        v-for="(q, index) in filteredQuestions"
        :key="index"
        class="d-flex justify-content-between align-items-start p-3 mb-2 border rounded bg-white"
      >
        <div>
          <p class="mb-1 fw-semibold">{{ q.text }}</p>
          <small class="text-muted">Anonymous</small>
        </div>
        <div class="text-end">
          <button class="btn btn-sm btn-outline-secondary" disabled>
            👍 {{ q.likes }}
          </button>
        </div>
      </div>
    </div>
    <div v-else class="alert alert-info">아직 질문이 없습니다.</div>
  </div>
</template>

<script>
export default {
  name: 'ProfessorRealtimeQuestion',
  data() {
    return {
      recognition: null,
      recognitionStatus: '정지됨',
      sentenceBuffer: '',
      sentenceCount: 0,
      tab: 'recent',
      questions: []
    };
  },
  computed: {
    filteredQuestions() {
      return [...this.questions].sort((a, b) => {
        if (this.tab === 'popular') return b.likes - a.likes;
        return new Date(b.created_at) - new Date(a.created_at);
      });
    }
  },
  mounted() {
    this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      try {
        const res = await fetch(`https://project2025-backend.onrender.com/questions`);
        this.questions = await res.json();
      } catch (err) {
        console.error('질문 불러오기 실패:', err);
      }
    },
    startRecognition() {
      if (!('webkitSpeechRecognition' in window)) {
        alert('음성 인식을 지원하지 않는 브라우저입니다.');
        return;
      }
      const SpeechRecognition = window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'ko-KR';
      this.recognition.continuous = true;
      this.recognition.interimResults = false;

      this.recognition.onstart = () => {
        this.recognitionStatus = '음성 인식 중 🎙️';
      };

      this.recognition.onresult = async (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript.trim();
          if (event.results[i].isFinal && transcript) {
            this.sentenceBuffer += transcript + ' ';
            this.sentenceCount++;

            try {
              await fetch(`https://project2025-backend.onrender.com/vad/upload_text_chunk`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: transcript })
              });

              if (transcript.includes('질문')) {
                await fetch(`https://project2025-backend.onrender.com/vad/trigger_question_generation`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({})
                });
              }
            } catch (err) {
              console.error('텍스트 전송 또는 질문 트리거 실패:', err);
            }
          }
        }
      };

      this.recognition.onerror = (e) => {
        console.error('음성 인식 오류:', e);
        this.recognitionStatus = '오류 발생';
      };

      this.recognition.onend = () => {
        this.recognitionStatus = '정지됨';
      };

      this.recognition.start();
    },
    stopRecognition() {
      if (this.recognition) {
        this.recognition.stop();
        this.recognitionStatus = '정지됨';
      }
    }
  }
}
</script>

<style scoped>
body {
  background-color: #f8f9fa;
}
</style>
