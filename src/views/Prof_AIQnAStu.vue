<script>
/* global webkitSpeechRecognition */
export default {
  name: 'ProfessorRealtimeQuestion',
  data() {
    return {
      recognition: null,
      recognitionStatus: '정지됨',
      results: [],
      pendingChunks: [],
      isSending: false,
    };
  },
  methods: {
    startRecognition() {
      if (!('webkitSpeechRecognition' in window)) {
        alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
        return;
      }

      if (this.recognition && this.recognition.running) {
        return; // 중복 방지
      }

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
            this.pendingChunks.push(transcript);
            this.flushTextQueue();
          }
        }
      };

      this.recognition.onerror = (event) => {
        console.error('음성 인식 오류:', event.error);
      };

      this.recognition.onend = () => {
        this.recognitionStatus = '정지됨';
      };

      this.recognition.start();
    },

    stopRecognition() {
      if (this.recognition) {
        this.recognition.stop();
      }
      this.recognitionStatus = '정지됨';
    },

    async flushTextQueue() {
      if (this.isSending || this.pendingChunks.length === 0) return;
      this.isSending = true;

      while (this.pendingChunks.length > 0) {
        const chunk = this.pendingChunks.shift();
        await this.sendTextChunk(chunk);
      }

      this.isSending = false;
    },

    async sendTextChunk(textChunk) {
      try {
        const response = await fetch(`https://project2025-backend.onrender.com/vad/upload_text_chunk`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: textChunk }),
        });

        if (!response.ok) throw new Error('질문 생성 실패');

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
