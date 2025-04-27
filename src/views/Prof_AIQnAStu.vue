<template>
  <div class="professor-aiqna-stu">
    <h2 class="text-center my-4">학생의 실시간 질문 사이언스 + 강의 노치</h2>

    <div class="btn-group d-flex justify-content-center mb-4">
      <button class="btn btn-primary m-2" @click="toggleRecognition">
        {{ recognitionStatus === '시작' ? '녹음 시작 버튼 확인' : '녹음 중지 버튼 확인' }} 🎙️
      </button>

      <button class="btn btn-danger m-2" @click="toggleScreenRecording">
        {{ isScreenRecording ? '화면 녹화 시작' : '화면 녹화 중지' }} 📹
      </button>
    </div>

    <div class="output-area text-center">
      <h4>✨ 생성된 질문</h4>
      <p>{{ generatedQuestion || '아직 생성된 질문이 없습니다.' }}</p>
    </div>

    <div v-if="uploadMessage" class="alert alert-info text-center mt-3">
      {{ uploadMessage }}
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
      generatedQuestion: '',
      isScreenRecording: false,
      mediaRecorder: null,
      screenStream: null,
      keywords: ['중요', '퀴즈', '요약'], // 키워드 목록
      uploadMessage: '' // 업로드 상태 메시지
    };
  },
  methods: {
    toggleRecognition() {
      if (!this.recognition) {
        if (!('webkitSpeechRecognition' in window)) {
          alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
          return;
        }
        this.recognition = new webkitSpeechRecognition();
        this.recognition.lang = 'ko-KR';
        this.recognition.continuous = true;

        this.recognition.onresult = (event) => {
          const transcript = event.results[event.results.length - 1][0].transcript.trim();
          console.log('인식된 텍스트:', transcript);
          this.generatedQuestion = transcript;

          // 키워드 감지
          this.keywords.forEach(keyword => {
            if (transcript.includes(keyword)) {
              console.log(`키워드 '${keyword}' 감지됨! 화면 캡처 시작.`);
              this.captureScreen();
            }
          });
        };

        this.recognition.onerror = (event) => {
          console.error('음성 인식 오류:', event.error);
        };
      }

      if (this.recognitionStatus === '정지됨') {
        this.recognition.start();
        this.recognitionStatus = '시작';
      } else {
        this.recognition.stop();
        this.recognitionStatus = '정지됨';
      }
    },

    async toggleScreenRecording() {
      if (!this.isScreenRecording) {
        try {
          this.screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
          this.mediaRecorder = new MediaRecorder(this.screenStream);

          this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
              this.uploadRecording(event.data);
            }
          };

          this.mediaRecorder.start();
          this.isScreenRecording = true;
        } catch (error) {
          console.error('화면 녹화 오류:', error);
        }
      } else {
        if (this.mediaRecorder) {
          this.mediaRecorder.stop();
        }
        if (this.screenStream) {
          this.screenStream.getTracks().forEach(track => track.stop());
        }
        this.isScreenRecording = false;
      }
    },

    uploadRecording(blob) {
      console.log('녹화 업로드 준비 중...', blob);
      // TODO: 서버로 녹화 파일 업로드하는 로직 추가 가능
    },

    async captureScreen() {
      try {
        const canvas = document.createElement('canvas');
        const videoTrack = this.screenStream.getVideoTracks()[0];
        const imageCapture = new ImageCapture(videoTrack);
        const bitmap = await imageCapture.grabFrame();

        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(bitmap, 0, 0);

        canvas.toBlob(blob => {
          console.log('화면 캡처 완료', blob);
          this.uploadScreenshot(blob);
        }, 'image/jpeg');
      } catch (error) {
        console.error('화면 캡처 오류:', error);
      }
    },

    async uploadScreenshot(blob) {
      const formData = new FormData();
      formData.append('file', blob, 'screenshot.jpg');

      try {
        const response = await fetch('/upload/screenshot', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          this.uploadMessage = '✅ 스크린샷 업로드 성공!';
          console.log('스크린샷 업로드 성공');
        } else {
          this.uploadMessage = '❌ 스크린샷 업로드 실패!';
          console.error('스크린샷 업로드 실패');
        }

        // 5초 뒤 알림 자동 삭제
        setTimeout(() => {
          this.uploadMessage = '';
        }, 5000);

      } catch (error) {
        this.uploadMessage = '❌ 스크린샷 업로드 중 오류 발생!';
        console.error('스크린샷 업로드 중 오류 발생:', error);

        setTimeout(() => {
          this.uploadMessage = '';
        }, 5000);
      }
    }
  }
};
</script>

<style scoped>
.professor-aiqna-stu {
  padding: 20px;
}
.output-area {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}
.alert {
  margin-top: 20px;
  font-weight: bold;
}
</style>
