
<template>
  <div>
    <h2>🎤 프론트 VAD + MediaRecorder (최종 안정화 버전)</h2>
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
    let mediaRecorder = null
    let audioChunks = []
    let vadController = null
    let audioSource = null

    const sendAudio = (blob) => {
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

    const setupVAD = (audioContext, source) => {
      vadController = vad(audioContext, source, {
        onVoiceStart: () => {
          console.log('🎙️ 음성 시작')
          if (mediaRecorder && mediaRecorder.state === 'inactive') {
            audioChunks = []
            mediaRecorder.start()
            console.log('▶️ MediaRecorder 시작')
          }
        },
        onVoiceStop: () => {
          console.log('🔇 음성 종료')
          if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop()
            console.log('⏹️ MediaRecorder 정지')
          }
        },
        interval: 300,
        voice_stop: 800,
      })
    }

    const startRecording = async () => {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
        console.log("✅ mediaStream 타입 확인:", mediaStream && mediaStream.constructor.name)

        await new Promise((resolve) => setTimeout(resolve, 200)) // 안정화 대기

        audioContext = new AudioContext()

        // ✅ AudioNode는 한 번만 생성하고 재사용
        if (!audioSource) {
          try {
            audioSource = audioContext.createMediaStreamSource(mediaStream)
            console.log("🎉 AudioSource 최초 생성 성공")
          } catch (err) {
            console.warn("⚠️ 기본 방식 실패, fallback 시도:", err)
            const fallbackStream = new MediaStream(mediaStream.getAudioTracks())
            audioSource = audioContext.createMediaStreamSource(fallbackStream)
            console.log("✅ fallback AudioSource 생성 성공")
          }
        }

        setupVAD(audioContext, audioSource)

        // MediaRecorder 세팅
        mediaRecorder = new MediaRecorder(mediaStream)
        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            audioChunks.push(e.data)
          }
        }

        mediaRecorder.onstop = () => {
          const blob = new Blob(audioChunks, { type: 'audio/webm' })
          sendAudio(blob)
        }

        isRecording.value = true
      } catch (err) {
        console.error('🎤 마이크 접근 실패:', err)
      }
    }

    const stopRecording = () => {
      if (vadController && vadController.stop) vadController.stop()
      if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop()
      if (mediaStream) mediaStream.getTracks().forEach(track => track.stop())
      if (audioContext) audioContext.close()
      audioSource = null // 반드시 해제
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
