<template>
    <div class="text-center mt-5">
      <h2>🎥 수업 녹화 & 음성 녹음</h2>
      <p class="text-muted">아래 버튼으로 수업을 시작하거나 종료하세요.</p>
  
      <!-- 화면 녹화 토글 버튼 -->
      <button class="btn btn-danger m-2" @click="toggleScreenRecording">
        {{ isScreenRecording ? "🛑 화면 녹화 중지" : "📹 화면 녹화 시작" }}
      </button>
  
      <!-- 오디오 녹음 토글 버튼 -->
      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isAudioRecording ? "🛑 녹음 중지" : "🎙️ 음성 녹음 시작" }}
      </button>
    </div>
  </template>
  
  <script>
  export default {
    name: "ProfessorLesson",
    data() {
      return {
        // 오디오 녹음 상태
        isAudioRecording: false,
        audioRecorder: null,
        audioStream: null,
        audioChunks: [],
  
        // 화면 녹화 상태
        isScreenRecording: false,
        screenRecorder: null,
        screenChunks: [],
      };
    },
    methods: {
      // 🎙️ 오디오 녹음 토글
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
            };
  
            this.audioRecorder.start();
            this.isAudioRecording = true;
            console.log("🎙️ 오디오 녹음 시작됨");
  
            this.audioStream.getAudioTracks()[0].addEventListener("ended", () => {
              if (this.isAudioRecording) {
                this.audioRecorder.stop();
                this.isAudioRecording = false;
                console.log("🛑 마이크 꺼짐 → 녹음 종료");
              }
            });
          } catch (err) {
            console.error("❌ 오디오 녹음 실패:", err);
          }
        } else {
          this.audioRecorder.stop();
          this.isAudioRecording = false;
          console.log("🛑 오디오 녹음 수동 중지됨");
        }
      },
  
      // 📹 화면 + 마이크 오디오 녹화 토글
      async toggleScreenRecording() {
        if (!this.isScreenRecording) {
          try {
            const displayStream = await navigator.mediaDevices.getDisplayMedia({
              video: true,
              audio: true, // 시스템 오디오 (브라우저에 따라 다름)
            });
  
            const micStream = await navigator.mediaDevices.getUserMedia({ audio: true }); // 마이크 오디오
  
            const combinedStream = new MediaStream([
              ...displayStream.getVideoTracks(),
              ...micStream.getAudioTracks(),
            ]);
  
            this.screenRecorder = new MediaRecorder(combinedStream);
            this.screenChunks = [];
  
            this.screenRecorder.ondataavailable = (e) => {
              if (e.data.size > 0) this.screenChunks.push(e.data);
            };
  
            this.screenRecorder.onstop = () => {
              const blob = new Blob(this.screenChunks, { type: "video/webm" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "screen-recording-with-audio.webm";
              a.click();
  
              displayStream.getTracks().forEach((track) => track.stop());
              micStream.getTracks().forEach((track) => track.stop());
            };
  
            this.screenRecorder.start();
            this.isScreenRecording = true;
            console.log("🔴 화면+마이크 녹화 시작됨");
  
            displayStream.getVideoTracks()[0].addEventListener("ended", () => {
              if (this.isScreenRecording) {
                this.screenRecorder.stop();
                this.isScreenRecording = false;
                console.log("🛑 화면 공유 종료 감지 → 녹화 종료");
              }
            });
          } catch (err) {
            console.error("❌ 화면+오디오 녹화 실패:", err);
          }
        } else {
          this.screenRecorder.stop();
          this.isScreenRecording = false;
          console.log("🛑 화면+마이크 녹화 수동 중지됨");
        }
      },
    },
  };
  </script>
  