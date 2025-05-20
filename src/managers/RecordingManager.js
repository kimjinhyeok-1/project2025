import { uploadSnapshot, captureScreenshot } from "@/api/snapshotService";

class RecordingManager {
  constructor(mode = 'keyword') {
    this.mode = mode; // 'keyword' | 'segment'
    this.isRecording = false;
    this.isRecognizing = false;
    this.audioRecorder = null;
    this.audioStream = null;
    this.displayStream = null;
    this.recognition = null;
    this.listeners = [];
    this.segmentListeners = [];
    this.lectureId = null;

    this.triggerKeywords = ["보면", "보게 되면", "이 부분", "이걸 보면", "코드", "화면", "여기", "이쪽"];

    // VAD-like segment buffer
    this.segmentBuffer = "";
    this.lastTranscriptTime = null;
    this.segmentSilenceTimeout = 3000; // 3초 침묵 시 segment 처리
  }

  setLectureId(id) {
    this.lectureId = id;
  }

  getLectureId() {
    return this.lectureId;
  }

  setMode(mode) {
    this.mode = mode;
  }

  subscribe(callback) {
    this.listeners.push(callback);
    callback(this.isRecording);
  }

  onSegment(callback) {
    this.segmentListeners.push(callback);
  }

  notify() {
    this.listeners.forEach((cb) => cb(this.isRecording));
  }

  notifySegment(segment) {
    this.segmentListeners.forEach((cb) => cb(segment));
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

    this.audioRecorder?.stop();
    this.audioStream?.getTracks().forEach((track) => track.stop());
    this.displayStream?.getTracks().forEach((track) => track.stop());
    this.stopRecognition();

    this.isRecording = false;
    this.notify();

    console.log("🛑 Recording Stopped.");
  }

  startRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("❌ 음성 인식을 지원하지 않는 브라우저입니다.");
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = "ko-KR";

    this.recognition.onresult = (event) => {
      const results = event.results;
      const transcript = results[results.length - 1][0].transcript.trim();
      const isFinal = results[results.length - 1].isFinal;

      if (this.mode === 'keyword') {
        this.handleKeywordRecognition(transcript);
      } else if (this.mode === 'segment') {
        this.handleSegmentRecognition(transcript, isFinal);
      }
    };

    this.recognition.start();
    this.isRecognizing = true;
  }

  stopRecognition() {
    if (this.recognition) {
      this.recognition.stop();
      this.isRecognizing = false;
    }
  }

  handleKeywordRecognition(transcript) {
    const found = this.triggerKeywords.find(keyword => transcript.includes(keyword));
    if (found) {
      console.log("🔔 키워드 감지:", found);
      this.captureAndSend(transcript);
    }
  }

  handleSegmentRecognition(transcript, isFinal) {
    const now = Date.now();
    this.segmentBuffer += transcript + " ";
    this.lastTranscriptTime = now;

    if (isFinal) {
      setTimeout(() => {
        const elapsed = Date.now() - this.lastTranscriptTime;
        if (elapsed >= this.segmentSilenceTimeout && this.segmentBuffer.trim()) {
          const segment = this.segmentBuffer.trim();
          console.log("🧠 문단 생성:", segment);
          this.notifySegment(segment);
          this.segmentBuffer = "";
        }
      }, this.segmentSilenceTimeout + 100);
    }
  }

  async captureAndSend(transcript) {
    const screenshot_base64 = await captureScreenshot(this.displayStream);
    const timestamp = new Date().toISOString();
    await uploadSnapshot({ timestamp, transcript, screenshot_base64 });
  }
}

export default new RecordingManager();
