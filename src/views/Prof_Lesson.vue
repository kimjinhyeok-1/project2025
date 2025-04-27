<template>
  <div class="lecture-container text-center mt-5">
    <h2>🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted">녹음 중 키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드에 전송됩니다.</p>

    <div class="btn-group mt-4">
      <button class="btn btn-danger m-2" @click="toggleScreenRecording">
        {{ isScreenRecording ? "🔝 화면 녹화 중지" : "📹 화면 녹화 시작" }}
      </button>

      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isAudioRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>

      <button class="btn btn-warning m-2" @click="testOptions">
        🧪 OPTIONS 테스트
      </button>
    </div>
  </div>
</template>

<script>
import { uploadSnapshot, testOptionsRequest } from "@/api/snapshotService"

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isAudioRecording: false,
      isScreenRecording: false,
      audioRecorder: null,
      audioStream: null,
      audioChunks: [],
      recognition: null,
      displayStream: null,
      triggerKeywords: ["보면", "보게 되면", "이 부분", "이걸 보면", "코드", "화면", "여기", "이쪽"],
    }
  },
  methods: {
    async toggleAudioRecording() {
      if (!this.isAudioRecording) {
        try {
          this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
          this.audioRecorder = new MediaRecorder(this.audioStream)
          this.audioChunks = []

          this.audioRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) this.audioChunks.push(e.data)
          }

          this.audioRecorder.onstop = () => {
            if (this.audioStream) {
              this.audioStream.getTracks().forEach((track) => track.stop())
              this.audioStream = null
            }

            if (this.displayStream) {
              this.displayStream.getTracks().forEach((track) => track.stop())
              this.displayStream = null
            }
          }

          this.displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true })
          this.audioRecorder.start()
          this.isAudioRecording = true
          this.startRecognition()
        } catch (err) {
          console.error("❌ 오디오 녹음 또는 화면 캡처 권한 실패:", err)
        }
      } else {
        this.audioRecorder.stop()
        this.isAudioRecording = false
        this.stopRecognition()
      }
    },

    toggleScreenRecording() {
      // 선택적 구현
    },

    startRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (!SpeechRecognition) {
        alert("브라우저가 음성 인식을 지원하지 않아요 🙁")
        return
      }

      this.recognition = new SpeechRecognition()
      this.recognition.lang = "ko-KR"
      this.recognition.continuous = true
      this.recognition.interimResults = false

      this.recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript
        console.log("🎙️ 음성 인식 결과:", transcript)

        const hit = this.triggerKeywords.some((kw) => transcript.includes(kw)) ||
                    /보.*면|코드|화면|여기|이 부분|이\uc쪽/.test(transcript)

        if (hit) {
          this.takeScreenshotAndUpload(transcript)
        } else {
          this.sendTranscriptOnly(transcript)
        }
      }

      this.recognition.onerror = (event) => {
        console.error("음성 인식 에러:", event.error)
      }

      this.recognition.start()
    },

    stopRecognition() {
      if (this.recognition) {
        this.recognition.stop()
        this.recognition = null
      }
    },

    async sendTranscriptOnly(transcript) {
      if (!transcript || transcript.trim() === "") {
        console.error("❌ transcript가 비어있어서 전송 중단");
        return;
      }

      try {
        const now = new Date();
        const timestamp = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")} ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;

        await uploadSnapshot({
          timestamp,
          transcript,
          screenshot_base64: "", // 빈 문자열이라도 항상 채워서 보내기
        });

        console.log("✅ 텍스트만 전송 완료");
      } catch (err) {
        console.error("❌ 텍스트만 전송 실패:", err.response?.data || err.message || err);
      }
    },

    async takeScreenshotAndUpload(transcript) {
      if (!transcript || transcript.trim() === "") {
        console.error("❌ transcript가 비어있어서 전송 중단");
        return;
      }

      try {
        if (!this.displayStream) {
          console.error("❌ displayStream 없음, 기본 스크린샷 빈 문자열로 보냄");
          const now = new Date();
          const timestamp = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")} ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;

          await uploadSnapshot({
            timestamp,
            transcript,
            screenshot_base64: "",
          });
          return;
        }

        const track = this.displayStream.getVideoTracks()[0];
        const imageCapture = new ImageCapture(track);
        const bitmap = await imageCapture.grabFrame();

        const canvas = document.createElement("canvas");
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(bitmap, 0, 0);
        const imageBase64 = canvas.toDataURL("image/png");

        const now = new Date();
        const timestamp = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, "0")}-${now.getDate().toString().padStart(2, "0")} ${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;

        await uploadSnapshot({
          timestamp,
          transcript,
          screenshot_base64: imageBase64,
        });

        console.log("✅ 백엔드에 스크린샷 전송 완료");
      } catch (err) {
        console.error("❌ 스크린샷 전송 실패:", err.response?.data || err.message || err);
      }
    },

    async testOptions() {
      await testOptionsRequest();
    }
  }
}
</script>

<style scoped>
.lecture-container {
  max-width: 900px;
  margin: auto;
  padding: 30px;
}
</style>
