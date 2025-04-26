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
    </div>
  </template>
  
  <script>
  export default {
    name: 'ProfessorRealtimeQuestion',
    data() {
      return {
        recognition: null,
        transcript: '',
        recognitionStatus: '정지됨'
      };
    },
    methods: {
      startRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
          alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
          return;
        }
  
        this.recognition = new webkitSpeechRecognition();
        this.recognition.lang = 'ko-KR'; // 한국어로 설정
        this.recognition.interimResults = true; // 중간 결과 표시
        this.recognition.continuous = true; // 연속 듣기
  
        this.recognition.onstart = () => {
          this.recognitionStatus = '음성 인식 중 🎙️';
        };
  
        this.recognition.onresult = (event) => {
          let interimTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptPiece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              this.transcript += transcriptPiece + ' ';
            } else {
              interimTranscript += transcriptPiece;
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
      }
    }
  };
  </script>
  
  <style scoped>
  button {
    transition: background-color 0.3s;
  }
  </style>
  