// ✅ VAD 기반 세그먼트 인식이 추가된 RecordingManager.js
import { uploadSnapshot } from "@/api/snapshotService";

class RecordingManager {
  constructor(mode = "keyword") {
    this.mode = mode; // 'keyword' 또는 'segment'
    this.isRecording = false;
    this.audioStream = null;
    this.recognition = null;
    this.listeners = [];
    this.segmentListeners = [];
    this.triggerKeywords = ["보면", "보게 되면", "이 부분", "이걸 보면", "코드", "화면", "여기", "이쪽"];
  }

  setMode(mode) {
    this.mode = mode;
  }

  onSegment(callback) {
    this.segmentListeners.push(callback);
  }

  notifySegment(text) {
    this.segmentListeners.forEach((cb) => cb(text));
  }

  async start() {
    this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.startRecognition();
    this.isRecording = true;
    console.log("🎙️ Recording started in mode:", this.mode);
  }

  stop() {
    this.recognition?.stop();
    this.audioStream?.getTracks().forEach((track) => track.stop());
    this.isRecording = false;
    console.log("🛑 Recording stopped.");
  }

  startRecognition() {
    const SpeechRecognition = window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.lang = "ko-KR";
    this.recognition.continuous = true;
    this.recognition.interimResults = false;

    this.recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript.trim();
        if (!transcript) continue;

        if (this.mode === "keyword") {
          if (this.triggerKeywords.some((k) => transcript.includes(k))) {
            console.log("🚨 키워드 트리거 감지:", transcript);
            uploadSnapshot({ transcript });
          }
        } else if (this.mode === "segment") {
          this.notifySegment(transcript);
        }
      }
    };

    this.recognition.start();
  }
}

const recordingManager = new RecordingManager();
export default recordingManager;
