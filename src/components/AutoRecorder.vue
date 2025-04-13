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
  
            const res = await fetch('http://localhost:8000/api/audio', {
              method: 'POST',
              body: formData,
            })
  
            const data = await res.json()
            question.value = data.question
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
  