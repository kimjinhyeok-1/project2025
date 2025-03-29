<template>
  <div class="lecture-container text-center mt-5">
    <h2>🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted">음성 인식 중 키워드가 감지되면 자동으로 화면이 백그라운드에서 캡처됩니다. 결과는 '수업 복습하기'에서 확인하세요.</p>

    <div class="btn-group mt-4">
      <button class="btn btn-danger m-2" @click="toggleScreenRecording">
        {{ isScreenRecording ? "🛑 화면 녹화 중지" : "📹 화면 녹화 시작" }}
      </button>

      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isAudioRecording ? "🛑 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProfessorLesson",
  data() {
    return {
      isAudioRecording: false,
      isScreenRecording: false,
      audioRecorder: null,
      audioStream: null,
      audioChunks: [],
      screenRecorder: null,
      screenChunks: [],
      recognition: null,
      triggerKeywords: ["보면", "보게 되면", "이 부분", "이걸 보면", "코드", "화면", "여기", "이쪽"],
      lastTranscript: "",
      displayStream: null, // 백그라운드 화면 스트림 저장용
    };
  },
  methods: {
    async toggleAudioRecording() {
      if (!this.isAudioRecording) {
        try {
          this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
          this.audioRecorder = new MediaRecorder(this.audioStream);
          this.audioChunks = [];

          this.audioRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) this.audioChunks.push(e.data);
          };

          this.audioRecorder.onstop = () => {
            const blob = new Blob(this.audioChunks, { type: "audio/webm" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "audio-recording.webm";
            a.click();

            if (this.audioStream) {
              this.audioStream.getTracks().forEach((track) => track.stop());
              this.audioStream = null;
            }

            if (this.displayStream) {
              this.displayStream.getTracks().forEach((track) => track.stop());
              this.displayStream = null;
            }
          };

          // 화면 공유 요청 (한 번만)
          this.displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });

          this.audioRecorder.start();
          this.isAudioRecording = true;

          this.startRecognition();

        } catch (err) {
          console.error("❌ 오디오 녹음 또는 화면 캡처 권한 실패:", err);
        }
      } else {
        this.audioRecorder.stop();
        this.isAudioRecording = false;
        this.stopRecognition();
      }
    },

    async toggleScreenRecording() {
      // 선택적: 일반 화면+오디오 녹화 기능 (옵션)
    },

    startRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert("브라우저가 음성 인식을 지원하지 않아요 🙁");
        return;
      }

      this.recognition = new SpeechRecognition();
      this.recognition.lang = "ko-KR";
      this.recognition.continuous = true;
      this.recognition.interimResults = false;

      this.recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        this.lastTranscript = transcript;
        console.log("🎤 음성 인식 결과:", transcript);

        const hit = this.triggerKeywords.some((kw) => transcript.includes(kw)) ||
                    /보.*면|코드|화면|여기|이 부분|이쪽/.test(transcript);

        if (hit) {
          this.takeScreenshot(transcript);
        }
      };

      this.recognition.onerror = (event) => {
        console.error("음성 인식 에러:", event.error);
      };

      this.recognition.start();
    },

    stopRecognition() {
      if (this.recognition) {
        this.recognition.stop();
        this.recognition = null;
      }
    },

    async takeScreenshot(transcript) {
      try {
        if (!this.displayStream) return;

        const track = this.displayStream.getVideoTracks()[0];
        const imageCapture = new ImageCapture(track);
        const bitmap = await imageCapture.grabFrame();

        const canvas = document.createElement("canvas");
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(bitmap, 0, 0);
        const imageUrl = canvas.toDataURL("image/png");

        const now = new Date().toLocaleTimeString();

        const log = JSON.parse(sessionStorage.getItem("screenshotLog") || "[]");
        log.push({ screenshot: imageUrl, timestamp: now, transcript });
        sessionStorage.setItem("screenshotLog", JSON.stringify(log));

      } catch (err) {
        console.error("❌ 스크린샷 실패:", err);
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
