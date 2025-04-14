<template>
  <div>
    <h2>🎤 실시간 음성 녹음 + 전송 테스트</h2>
    <button @click="startRecording" :disabled="isRecording">녹음 시작</button>
    <button @click="stopRecording" :disabled="!isRecording">녹음 종료</button>
    <p v-if="question">🧠 AI 질문: {{ question }}</p>
  </div>
</template>

<script>
import { ref } from 'vue'

// ✅ 백엔드의 POST API 주소 정확히 반영
const BASE_URL = 'https://project2025-backend.onrender.com/vad/upload_audio_chunk'

export default {
  setup() {
    const isRecording = ref(false)
    const question = ref('')
    let mediaRecorder = null
    let audioChunks = []

    const startRecording = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorder = new MediaRecorder(stream)

        mediaRecorder.ondataavailable = (e) => {
          audioChunks.push(e.data)
        }

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }) // ✅ webm 형식으로 설정
          audioChunks = []

          const formData = new FormData()
          formData.append('file', audioBlob, 'chunk.webm') // ✅ 확장자도 webm으로 통일

          try {
            console.log("📤 업로드 시작")
            console.log("👉 실제 전송 주소:", BASE_URL)
            console.log("📤 POST 전송 직전");
            
            const res = await fetch(BASE_URL, {
              method: 'POST', // ✅ 반드시 POST로 명시
              body: formData,
              credentials: 'include'
            })

            const data = await res.json()
            console.log("📥 응답 도착:", data)

            question.value = data.question || '❔ 질문 없음'
          } catch (err) {
            console.error("❌ 전송 중 에러 발생:", err)
          }
        }

        mediaRecorder.start()
        isRecording.value = true

        const interval = setInterval(() => {
          if (!isRecording.value) {
            clearInterval(interval)
            return
          }
          mediaRecorder.stop()
          mediaRecorder.start()
        }, 5000) // ✅ 5초 간격 자동 chunk

      } catch (err) {
        console.error('🎤 마이크 접근 실패:', err)
      }
    }

    const stopRecording = () => {
      if (mediaRecorder && isRecording.value) {
        isRecording.value = false
        mediaRecorder.stop()
      }
    }

    return {
      startRecording,
      stopRecording,
      isRecording,
      question,
    }
  }
}
</script>
