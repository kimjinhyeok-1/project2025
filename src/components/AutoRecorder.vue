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
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
          audioChunks = []

          const formData = new FormData()
          formData.append('file', audioBlob, 'chunk.wav')

          try {
            // ✅ 여기에 백엔드 주소를 너희 팀의 실제 Render 주소로 바꿔줘
            const res = await fetch(BASE_URL, {
              method: 'POST',
              body: formData,
            })

            const data = await res.json()
            question.value = data.question
          } catch (err) {
            console.warn('⚠️ 백엔드 연결 실패 또는 응답 오류:', err)
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
        }, 5000)

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
