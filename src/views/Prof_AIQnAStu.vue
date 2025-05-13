<template>
  <div class="lecture-container text-center mt-5">
    <h2>🎤 실시간 질문 시연 (VAD 단위)</h2>
    <p class="text-muted">음성 인식 버튼을 누르면 교수자의의 음성을 바탕으로 문단 및 질문이 자동 생성됩니다.</p>

    <div class="btn-group mt-4">
      <button @click="startRecognition" class="btn btn-primary m-2">🎙️ 음성 인식 시작</button>
      <button @click="stopRecognition" class="btn btn-danger m-2">🛑 음성 인식 중지</button>
    </div>

    <div class="mt-4">
      <p>현재 상태: <strong>{{ recognitionStatus }}</strong></p>
    </div>

    <div v-if="results.length" class="alert alert-success mt-5 text-start" style="white-space: pre-line;">
      <h5>🧠 생성된 문단 및 예상 질문</h5>
      <div v-for="(item, index) in results" :key="index" class="mb-4">
        <p class="fw-bold">{{ item.paragraph }}</p>
        <ul class="list-group list-group-flush mt-3">
          <li v-for="(question, qIndex) in item.questions" :key="qIndex" class="list-group-item">
            {{ question }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
/* global webkitSpeechRecognition */
export default {
  name: 'ProfessorRealtimeQuestion',
  data() {
    return {
      recognition: null,
      recognitionStatus: '정지됨',
      results: [],
      sentenceBuffer: '',
      sentenceCount: 0,
      isSending: false,
      SENTENCE_LIMIT: 3,
      CHAR_LIMIT: 300,
    };
  },
  methods: {
    startRecognition() {
      if (!('webkitSpeechRecognition' in window)) {
        alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
        return;
      }

      if (this.recognition && this.recognition.running) return;

      this.recognition = new webkitSpeechRecognition();
      this.recognition.lang = 'ko-KR';
      this.recognition.interimResults = false;
      this.recognition.continuous = true;

      this.recognition.onstart = () => {
        this.recognitionStatus = '음성 인식 중 🎙️';
      };

      this.recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript.trim();
          if (event.results[i].isFinal && transcript) {
            this.sentenceBuffer += transcript + ' ';
            this.sentenceCount += 1;

            if (
              this.sentenceCount >= this.SENTENCE_LIMIT ||
              this.sentenceBuffer.length >= this.CHAR_LIMIT
            ) {
              const paragraph = this.sentenceBuffer.trim();
              this.sendTextChunk(paragraph);
              this.sentenceBuffer = '';
              this.sentenceCount = 0;
            }
          }
        }
      };

      this.recognition.onerror = (event) => {
        console.error('음성 인식 오류:', event.error);
      };

      this.recognition.onend = () => {
        this.recognitionStatus = '정지됨';
        // 남은 문장 버퍼 전송
        if (this.sentenceBuffer.trim().length > 0) {
          this.sendTextChunk(this.sentenceBuffer.trim());
          this.sentenceBuffer = '';
          this.sentenceCount = 0;
        }
      };

      this.recognition.start();
    },

    stopRecognition() {
      if (this.recognition) this.recognition.stop();
      this.recognitionStatus = '정지됨';
    },

    async sendTextChunk(textChunk) {
      try {
        const payload = { text: textChunk };
        console.log('📤 전송할 문단:', payload);

        const response = await fetch('https://project2025-backend.onrender.com/vad/upload_text_chunk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ 백엔드 응답 에러 본문:', errorText);
          throw new Error('질문 생성 실패');
        }

        const data = await response.json();
        if (data.results) {
          this.results.push(...data.results);
        }
      } catch (error) {
        console.error('❌ 질문 생성 오류:', error);
        alert('질문 생성에 실패했습니다.');
      }
    },
  },
};
</script>

<style scoped>
.lecture-container {
  max-width: 900px;
  margin: auto;
  padding: 30px;
}
</style>
