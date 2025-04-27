<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">실시간 질문 시연 (VAD 단위)</h1>

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
    </div>

    <div v-if="results.length" class="mt-6">
      <h2 class="text-2xl font-semibold mb-4">생성된 문단 및 예상 질문</h2>
      <div v-for="(item, index) in results" :key="index" class="mb-6 p-4 border rounded bg-yellow-100">
        <p class="font-medium mb-2">{{ item.paragraph }}</p>
        <ul class="list-disc ml-6">
          <li v-for="(question, qIndex) in item.questions" :key="qIndex">{{ question }}</li>
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
      results: []
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
      this.recognition.interimResults = false; // VAD처럼 문장 단위 확정만 받기
      this.recognition.continuous = true;

      this.recognition.onstart = () => {
        this.recognitionStatus = '음성 인식 중 🎙️';
      };

      this.recognition.onresult = async (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcriptPiece = event.results[i][0].transcript.trim();
          if (event.results[i].isFinal && transcriptPiece) {
            await this.sendTextChunk(transcriptPiece);
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
    async sendTextChunk(textChunk) {
      try {
        const response = await fetch('https://project2025-backend.onrender.com/vad/upload_text_chunk', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: textChunk }),
        });

        if (!response.ok) {
          throw new Error('질문 생성 실패');
        }

        const data = await response.json();
        if (data.results) {
          this.results.push(...data.results); // 결과를 누적 표시
        }
      } catch (error) {
        console.error(error);
        alert('질문 생성에 실패했습니다.');
      }
    }
  }
};
</script>

<style scoped>
button {
  transition: background-color 0.3s;
}
</style>
