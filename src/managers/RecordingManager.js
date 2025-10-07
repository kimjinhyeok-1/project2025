import { uploadSnapshot, captureScreenshot } from "@/api/snapshotService";

class RecordingManager {
  constructor() {
    this.isRecording = false;
    this.isRecognizing = false;
    this.audioRecorder = null;
    this.audioStream = null;
    this.displayStream = null;
    this.recognition = null;
    this.listeners = [];
    this.transcriptListeners = [];
    this.lectureId = null;

    this.triggerKeywords = [
      "보면", "보게 되면", "이 부분", "이걸 보면", "코드", "화면", "여기", "이쪽"
    ];

    this.restartDelayMs = 200; // 음성 인식 재연결 딜레이
  }

  setLectureId(id) {
    this.lectureId = id;
  }

  getLectureId() {
    return this.lectureId;
  }

  subscribe(callback) {
    this.listeners.push(callback);
    callback(this.isRecording);
  }

  notify() {
    this.listeners.forEach((cb) => cb(this.isRecording));
  }

  subscribeToTranscript(cb) {
    this.transcriptListeners.push(cb);
  }

  unsubscribeFromTranscript(cb) {
    this.transcriptListeners = this.transcriptListeners.filter(fn => fn !== cb);
  }

  notifyTranscriptListeners(transcript) {
    this.transcriptListeners.forEach(cb => cb(transcript));
  }

  async startRecording() {
    if (this.isRecording) return;

    try {
      this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });

      this.audioRecorder = new MediaRecorder(this.audioStream);
      this.audioRecorder.start();

      this.startRecognition();
      this.isRecording = true;
      this.notify();

      console.log("🎙️ Recording Started.");
    } catch (error) {
      console.error("❌ 녹음 시작 실패:", error);
    }
  }

  stopRecording() {
    if (!this.isRecording) return;

    try { this.audioRecorder?.stop(); } catch (e) {}
    try { this.audioStream?.getTracks().forEach(track => track.stop()); } catch (e) {}
    try { this.displayStream?.getTracks().forEach(track => track.stop()); } catch (e) {}

    this.stopRecognition();

    this.isRecording = false;
    this.notify();

    console.log("🔚 Recording Stopped.");
  }

  startRecognition() {
    if (this.isRecognizing) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("이 브라우저는 음성 인식을 지원하지 않습니다.");
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.lang = "ko-KR";
    this.recognition.continuous = true;
    this.recognition.interimResults = false;

    this.recognition.onresult = async (event) => {
      try {
        const raw = event.results[event.results.length - 1][0].transcript || "";
        const transcript = raw.trim();
        console.log("🎤 인식된 문장:", transcript);

        this.notifyTranscriptListeners(transcript);

        const hasKeyword = this.triggerKeywords.some(kw => transcript.includes(kw));
        let imageBase64 = "";

        if (hasKeyword && this.displayStream) {
          imageBase64 = await captureScreenshot(this.displayStream);
        }

        await uploadSnapshot({
          transcript,
          screenshot_base64: imageBase64,
          isKeywordTriggered: hasKeyword
        });
      } catch (err) {
        console.error("❌ 스냅샷 업로드 실패:", err);
      }
    };

    // ⛑️ 핵심 수정: 즉시 재시작 금지. 에러 시 abort만 하고, 재시작은 onend에서 수행.
    this.recognition.onerror = (event) => {
      console.error("🎙️ 음성 인식 에러:", event.error);
      if (event.error === "no-speech" || event.error === "network" || event.error === "aborted" || event.error === "audio-capture") {
        try { this.recognition.abort(); } catch (e) {}
      }
    };

    // ⛑️ 핵심 수정: 종료 이벤트에서만 재시작을 담당
    this.recognition.onend = () => {
      this.isRecognizing = false;
      if (this.isRecording) {
        setTimeout(() => this.reconnectRecognition(), this.restartDelayMs);
      }
    };

    try {
      this.recognition.start();
      this.isRecognizing = true;
    } catch (e) {
      console.error("❌ 음성 인식 시작 실패:", e);
      this.isRecognizing = false;
    }
  }

  stopRecognition() {
    if (this.recognition) {
      try { this.recognition.onend = null; } catch (e) {}
      try { this.recognition.stop(); } catch (e) {}
      try { this.recognition.abort(); } catch (e) {}
      this.recognition = null;
    }
    this.isRecognizing = false;
  }

  reconnectRecognition() {
    if (this.isRecording && !this.isRecognizing) {
      console.log("🎙️ 음성 인식 재연결 시도");
      this.startRecognition();
    }
  }

  getState() {
    return {
      isRecording: this.isRecording
    };
  }
}

const recordingManager = new RecordingManager();
export default recordingManager;
