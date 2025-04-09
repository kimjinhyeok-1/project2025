<template>
  <div class="lecture-container text-center mt-5">
    <h2>🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted">녹음 중 키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드에 전송됩니다.</p>

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
import { uploadSnapshot } from "@/api/snapshotService" // ✅ 새로 만든 파일에서 가져옴

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
            const blob = new Blob(this.audioChunks, { type: "audio/webm" })
            const url = URL.createObjectURL(blob)
            const a = document.createElement("a")
            a.href = url
            a.download = "audio-recording.webm"
            a.click()

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
      // 선택적: 화면 녹화 기능 미구현
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
        console.log("🎤 음성 인식 결과:", transcript)

        const hit = this.triggerKeywords.some((kw) => transcript.includes(kw)) ||
                    /보.*면|코드|화면|여기|이 부분|이쪽/.test(transcript)

        if (hit) {
          this.takeScreenshotAndUpload(transcript)
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

    async takeScreenshotAndUpload(transcript) {
      try {
        if (!this.displayStream) return

        const track = this.displayStream.getVideoTracks()[0]
        const imageCapture = new ImageCapture(track)
        const bitmap = await imageCapture.grabFrame()

        const canvas = document.createElement("canvas")
        canvas.width = bitmap.width
        canvas.height = bitmap.height
        const ctx = canvas.getContext("2d")
        ctx.drawImage(bitmap, 0, 0)
        const imageBase64 = canvas.toDataURL("image/png")

        const now = new Date()
        const timestamp = now.toISOString().slice(0, 19).replace("T", " ") // "YYYY-MM-DD HH:MM:SS"

        await uploadSnapshot({
          timestamp,
          transcript,
          screenshot_base64: imageBase64
        })

        console.log("✅ 백엔드에 스냅샷 업로드 완료")

      } catch (err) {
        console.error("❌ 스크린샷 업로드 실패:", err)
      }
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
