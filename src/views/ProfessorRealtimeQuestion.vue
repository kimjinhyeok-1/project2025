<template>
    <div class="p-6">
      <h1 class="text-3xl font-bold mb-6">실시간 질문 시연</h1>
      
      <div class="mb-4">
        <button @click="startVAD" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded mr-2">
          음성 감지 시작
        </button>
        <button @click="stopVAD" class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded">
          음성 감지 중지
        </button>
      </div>
  
      <div class="mt-4">
        <p>현재 상태: <strong>{{ vadStatus }}</strong></p>
      </div>
    </div>
  </template>
  
  <script>
  import { WebRTCVoiceActivityDetector } from '@ricky0123/vad-web';
  
  export default {
    name: 'ProfessorRealtimeQuestion',
    data() {
      return {
        vad: null,
        vadStatus: '정지됨', // 상태 표시: 정지됨, 음성 감지중, 무음 상태
      };
    },
    methods: {
      async startVAD() {
        if (this.vad) {
          this.vad.stop();
        }
  
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  
        this.vad = new WebRTCVoiceActivityDetector(stream, (event) => {
          if (event.eventType === 'voice') {
            this.vadStatus = '음성 감지됨 🎤';
            console.log('음성 감지됨!');
          } else if (event.eventType === 'silence') {
            this.vadStatus = '무음 상태 🤫';
            console.log('무음 상태!');
          }
        }, {
          positiveSpeechThreshold: 0.9,
          negativeSpeechThreshold: 0.8,
          minSpeechFrames: 5,
          preSpeechPadFrames: 10
        });
  
        this.vad.start();
        this.vadStatus = '음성 감지 시작됨 🎙️';
      },
      stopVAD() {
        if (this.vad) {
          this.vad.stop();
          this.vad = null;
        }
        this.vadStatus = '정지됨';
      }
    }
  };
  </script>
  
  <style scoped>
  button {
    transition: background-color 0.3s;
  }
  </style>
  