import { uploadSnapshot, captureScreenshot } from "@/api/snapshotService";

class RecordingManager {
  constructor(mode = 'keyword') {
    this.mode = mode;
    this.isRecording = false;
    this.isRecognizing = false;
    this.audioRecorder = null;
    this.audioStream = null;
    this.displayStream = null;
    this.recognition = null;
    this.keywordListeners = [];
    this.segmentListeners = [];
    this.transcriptListeners = [];
    this.lectureId = null;
    this.segmentBuffer = "";
    this.lastTranscriptTime = null;
    this.segmentSilenceTimeout = 3000;
    this.triggerKeywords = ["보면", "보게 되면", "이 부분", "이걸 보면", "코드", "화면", "여기", "이쪽"];
  }

  setLectureId(id) { this.lectureId = id; }
  getLectureId() { return this.lectureId; }
  setMode(mode) { this.mode = mode; }

  onKeyword(cb) { this.keywordListeners.push(cb); }
  onSegment(cb) { this.segmentListeners.push(cb); }
  onTranscript(cb) { this.transcriptListeners.push(cb); }

  async startRecording() {
    if (this.isRecording) return;
    try {
      this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      this.audioRecorder = new MediaRecorder(this.audioStream);
      this.audioRecorder.start();
      this.startRecognition();
      this.isRecording = true;
      console.log("🎙️ Recording Started.");
    } catch (error) {
      console.error("❌ 녹음 시작 실패:", error);
    }
  }

  stopRecording() {
    if (!this.isRecording) return;
    this.audioRecorder?.stop();
    this.audioStream?.getTracks().forEach((t) => t.stop());
    this.displayStream?.getTracks().forEach((t) => t.stop());
    this.stopRecognition();
    this.isRecording = false;
    console.log("🛑 Recording Stopped.");
  }

  startRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return alert("❌ 브라우저가 STT를 지원하지 않습니다.");
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = "ko-KR";

    this.recognition.onresult = (event) => {
      const results = event.results;
      const transcript = results[results.length - 1][0].transcript.trim();
      const isFinal = results[results.length - 1].isFinal;

      this.transcriptListeners.forEach(cb => cb(transcript));
      if (this.mode === 'keyword') this.handleKeyword(transcript);
      else if (this.mode === 'segment') this.handleSegment(transcript, isFinal);
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

  handleKeyword(transcript) {
    const match = this.triggerKeywords.find(k => transcript.includes(k));
    if (match) {
      console.log("🔔 키워드 감지:", match);
      this.keywordListeners.forEach(cb => cb(transcript));
      this.captureAndSend(transcript);
    }
  }

  handleSegment(transcript, isFinal) {
    const now = Date.now();
    this.segmentBuffer += transcript + " ";
    this.lastTranscriptTime = now;

    if (isFinal) {
      setTimeout(() => {
        const elapsed = Date.now() - this.lastTranscriptTime;
        if (elapsed >= this.segmentSilenceTimeout && this.segmentBuffer.trim()) {
          const segment = this.segmentBuffer.trim();
          console.log("🧠 문단 생성:", segment);
          this.segmentListeners.forEach(cb => cb(segment));
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
