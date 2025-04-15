
<template>
  <div>
    <h2>🎤 실시간 음성 감지 + 전송 테스트 (프론트 VAD)</h2>
    <button @click="startRecording" :disabled="isRecording">녹음 시작</button>
    <button @click="stopRecording" :disabled="!isRecording">녹음 종료</button>
    <p v-if="question">🧠 AI 질문: {{ question }}</p>
  </div>
</template>

<script>
import { ref, onBeforeUnmount } from 'vue'
import vad from 'voice-activity-detection'

const BASE_URL = 'https://project2025-backend.onrender.com/vad/upload_audio_chunk'

export default {
  setup() {
    const isRecording = ref(false)
    const question = ref('')
    let audioContext = null
    let mediaStream = null

    const onSpeech = (audioBuffer) => {
      console.log("🗣️ 음성 감지됨. 백엔드로 전송 중...")

      const blob = new Blob([audioBuffer], { type: 'audio/webm' })
      const formData = new FormData()
      formData.append('file', blob, 'chunk.webm')

      fetch(BASE_URL, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })
        .then(res => res.json())
        .then(data => {
          console.log("📥 응답:", data)
          question.value = data.question || '❔ 질문 없음'
        })
        .catch(err => console.error('❌ 전송 실패:', err))
    }

    const startRecording = async () => {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
        console.log("🎤 mediaStream 확인:", mediaStream)

        if (!(mediaStream instanceof MediaStream)) {
          throw new Error("⛔ mediaStream이 MediaStream 타입이 아닙니다.")
        }

        audioContext = new AudioContext()
        const source = audioContext.createMediaStreamSource(mediaStream)

        vad(audioContext, source, {
          onVoiceStart: () => console.log('🎙️ 음성 시작'),
          onVoiceStop: () => console.log('🔇 음성 중지'),
          onUpdate: (val) => {
            if (val.voiceDetected) {
              console.log("🔍 음성 감지됨 (update)")
            }
          },
          onSpeech: onSpeech,
          interval: 500,
          voice_stop: 1000,
        })

        isRecording.value = true
      } catch (err) {
        console.error('🎤 마이크 접근 실패:', err)
      }
    }

    const stopRecording = () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
      }
      if (audioContext) {
        audioContext.close()
      }
      isRecording.value = false
    }

    onBeforeUnmount(() => {
      stopRecording()
    })

    return {
      startRecording,
      stopRecording,
      isRecording,
      question,
    }
  }
}
</script>
