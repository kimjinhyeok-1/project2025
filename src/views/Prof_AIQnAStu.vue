<script>
/* global webkitSpeechRecognition */
export default {
  name: 'ProfessorRealtimeQuestion',
  data() {
    return {
      recognition: null,
      transcript: '',
      recognitionStatus: '정지됨',
      generatedQuestion: ''
    };
  },
  methods: {
    startRecognition() {
      if (!('webkitSpeechRecognition' in window)) {
        alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
        return;
      }

      this.recognition = new webkitSpeechRecognition();
      this.recognition.lang = 'ko-KR';
      this.recognition.interimResults = true;
      this.recognition.continuous = true;

      this.recognition.onstart = () => {
        this.recognitionStatus = '음성 인식 중 🎙️';
      };

      this.recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPiece = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            this.transcript += transcriptPiece + ' ';
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
    async generateQuestion() {
      if (!this.transcript) {
        alert('먼저 음성을 인식해서 텍스트를 받아야 합니다!');
        return;
      }

      try {
        const response = await fetch('https://project2025-backend.onrender.com/vad/upload_text_chunk', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: this.transcript }), // 수정: text 키로 전송
        });

        if (!response.ok) {
          throw new Error('질문 생성 실패');
        }

        const data = await response.json();
        this.generatedQuestion = data.questions.join(' / '); // 예상 질문 리스트를 문자열로 표시
      } catch (error) {
        console.error(error);
        this.generatedQuestion = '질문 생성에 실패했습니다.';
      }
    }
  }
};
</script>

<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">실시간 질문 시연</h1>
    
    <div class="mb-4">
      <button @click="startRecognition" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded mr-2">
        음성 인식 시작
      </button>
      <button @click="stopRecognition" class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded">
        음성 인식 중지
      </button>
    </div>

    <div class="mt-4">
      <p>현재 상태: <strong>{{ recognitionStatus }}</strong></p>
      <p>🎤 인식된 텍스트:</p>
      <div class="bg-gray-100 p-4 rounded mt-2">
        {{ transcript }}
      </div>
    </div>

    <div class="mt-6">
      <button @click="generateQuestion" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
        AI 질문 생성하기
      </button>
    </div>

    <div v-if="generatedQuestion" class="mt-6 p-4 bg-yellow-100 rounded">
      <p>🧠 생성된 질문:</p>
      <p class="font-semibold">{{ generatedQuestion }}</p>
    </div>
  </div>
</template>

<style scoped>
button {
  transition: background-color 0.3s;
}
</style>
