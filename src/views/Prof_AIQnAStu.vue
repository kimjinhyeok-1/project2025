<template>
  <div class="container-fluid">
    <h1 class="h3 mb-4 text-gray-800">실시간 질문 시연 + 슬라이드 감지</h1>

    <!-- 음성 인식 제어 -->
    <div class="card shadow mb-4">
      <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-primary">음성 인식 제어</h6>
      </div>
      <div class="card-body">
        <button @click="startRecognition" class="btn btn-primary mr-2">
          <i class="fas fa-microphone"></i> 음성 인식 시작
        </button>
        <button @click="stopRecognition" class="btn btn-danger">
          <i class="fas fa-microphone-slash"></i> 음성 인식 중지
        </button>
        <div class="mt-4">
          <p>현재 상태: <strong>{{ recognitionStatus }}</strong></p>
        </div>
      </div>
    </div>

    <!-- 슬라이드 표시 -->
    <div class="card shadow mb-4">
      <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-info">슬라이드 감지 화면</h6>
      </div>
      <div class="card-body">
        <canvas ref="slideCanvas" width="640" height="480"></canvas>
        <p class="mt-2">감지된 슬라이드 전환 기록:</p>
        <ul>
          <li v-for="(log, idx) in slideChangeLog" :key="idx">
            {{ log.time }}초 - 슬라이드 {{ log.slide }}
          </li>
        </ul>
        <audio ref="audioRef" controls :src="audioSrc" />
      </div>
    </div>

    <!-- 결과 -->
    <div v-if="results.length" class="card shadow mb-4">
      <div class="card-header py-3">
        <h6 class="m-0 font-weight-bold text-success">생성된 문단 및 예상 질문</h6>
      </div>
      <div class="card-body">
        <div v-for="(item, index) in results" :key="index" class="mb-4">
          <div class="card mb-3">
            <div class="card-body">
              <p class="font-weight-bold">{{ item.paragraph }}</p>
              <ul class="list-group list-group-flush mt-3">
                <li v-for="(question, qIndex) in item.questions" :key="qIndex" class="list-group-item">
                  {{ question }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import pixelmatch from 'pixelmatch'
import * as pdfjsLib from 'pdfjs-dist'

pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js`

export default {
  name: 'ProfessorRealtimeQuestionSlide',
  data() {
    return {
      recognition: null,
      recognitionStatus: '정지됨',
      results: [],
      audioSrc: 'your-audio-file.mp3',
      slideChangeLog: [],
      prevImageData: null,
      pdf: null,
      currentPage: 1,
      intervalId: null,
    }
  },
  methods: {
    // 음성 인식
    startRecognition() {
      if (!('webkitSpeechRecognition' in window)) {
        alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
        return;
      }

      this.recognition = new webkitSpeechRecognition();
      this.recognition.lang = 'ko-KR';
      this.recognition.interimResults = false;
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
          this.results.push(...data.results);
        }
      } catch (error) {
        console.error(error);
        alert('질문 생성에 실패했습니다.');
      }
    },

    // 슬라이드 처리
    async loadPDF() {
      const loadingTask = pdfjsLib.getDocument('/sample.pdf'); // PDF 경로 수정
      this.pdf = await loadingTask.promise;
      await this.renderSlide(this.currentPage);
      this.startSlideChangeDetection();
    },
    async renderSlide(pageNum) {
      const canvas = this.$refs.slideCanvas;
      const context = canvas.getContext('2d');
      const page = await this.pdf.getPage(pageNum);
      const viewport = page.getViewport({ scale: 1.5 });

      canvas.width = viewport.width;
      canvas.height = viewport.height;

      await page.render({
        canvasContext: context,
        viewport: viewport,
      }).promise;
    },
    getImageData() {
      const canvas = this.$refs.slideCanvas;
      const context = canvas.getContext('2d');
      return context.getImageData(0, 0, canvas.width, canvas.height);
    },
    startSlideChangeDetection() {
      this.intervalId = setInterval(() => {
        const currentImageData = this.getImageData();

        if (this.prevImageData) {
          const diffCanvas = document.createElement('canvas');
          const diffContext = diffCanvas.getContext('2d');
          const diffImage = diffContext.createImageData(currentImageData.width, currentImageData.height);

          const diff = pixelmatch(
            this.prevImageData.data,
            currentImageData.data,
            diffImage.data,
            currentImageData.width,
            currentImageData.height,
            { threshold: 0.1 }
          );

          if (diff > 1000) {
            const time = this.$refs.audioRef?.currentTime || 0;
            this.slideChangeLog.push({
              time: time.toFixed(2),
              slide: this.currentPage,
            });
            console.log(`슬라이드 ${this.currentPage} 변경 감지 at ${time}s`);
          }
        }

        this.prevImageData = currentImageData;
      }, 2000);
    }
  },
  mounted() {
    this.loadPDF();
  },
  beforeUnmount() {
    clearInterval(this.intervalId);
  }
}
</script>

<style scoped>
button {
  transition: background-color 0.3s;
}
</style>
