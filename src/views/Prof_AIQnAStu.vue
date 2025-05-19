<template>
  <div class="container mt-5">
    <h2 class="mb-2">🎤 실시간 질문 생성 (교수용)</h2>
    <p class="text-muted">"질문"이라는 단어가 감지되면 이전까지의 내용을 기반으로 GPT 질문이 생성됩니다.</p>

    <div class="card p-4 mt-4">
      <div class="d-flex justify-content-between align-items-center">
        <span><strong>현재 상태:</strong> {{ recognitionStatus }}</span>
        <span class="text-muted small">누적 문장 수: {{ sentenceCount }}</span>
      </div>
    </div>

    <div class="mt-5">
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'popular' }" @click="tab = 'popular'">Popular</a>
        </li>
      </ul>

      <div v-if="filteredQuestions.length" class="mt-3">
        <div v-for="(q, index) in filteredQuestions" :key="index" class="card mb-3">
          <div class="card-body">
            <p class="mb-1">{{ q.text }}</p>
            <button class="btn btn-sm btn-outline-primary" disabled>
              👍 {{ q.likes }}
            </button>
          </div>
        </div>
      </div>
      <div v-else class="alert alert-info mt-4">아직 질문이 없습니다.</div>
    </div>
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
      questions: [] // { text: string, likes: number, created_at: Date }
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
    this.startRecognition();
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

      this.recognition = new webkitSpeechRecognition();
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
              await fetch(`https://project2025-backend.onrender.com/vad/stream_text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: transcript })
              });
            } catch (err) {
              console.error('텍스트 전송 실패:', err);
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
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 0.75rem;
  box-shadow: 0 0 0.25rem rgba(0,0,0,0.1);
}
</style>
