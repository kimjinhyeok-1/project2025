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

    // 음성 인식 재연결 딜레이(ms)
    this.restartDelayMs = 200;
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

    // 오디오 녹음기 정지
    if (this.audioRecorder && this.audioRecorder.state !== "inactive") {
      try {
        this.audioRecorder.stop();
      } catch (err) {
        console.debug("ℹ️ audioRecorder.stop() 실패(이미 정지 상태일 수 있음):", err);
      }
    }

    // 스트림 트랙 종료
    this.safeStopStream(this.audioStream);
    this.safeStopStream(this.displayStream);

    // 음성 인식 종료
    this.stopRecognition();

    this.isRecording = false;
    this.notify();

    console.log("🔚 Recording Stopped.");

    // ⏱️ 요약 시간 측정 시작(Prof_Lesson.vue에서 성공 시점에 읽어 사용)
    try {
      const t = (typeof performance !== "undefined" && typeof performance.now === "function")
        ? performance.now()
        : Date.now();
      sessionStorage.setItem("summary_timing_start", String(t));
      console.log("⏱️ 요약 타이머 시작:", t);
    } catch (err) {
      console.debug("ℹ️ 요약 타이머 시작 실패:", err);
    }
  }

  // 개별 스트림 안전 종료 유틸
  safeStopStream(stream) {
    if (!stream) return;
    try {
      const tracks = stream.getTracks ? stream.getTracks() : [];
      tracks.forEach((t) => {
        try {
          t.stop();
        } catch (err) {
          console.debug("ℹ️ 트랙 stop 실패(이미 정지 상태일 수 있음):", err);
        }
      });
    } catch (err) {
      console.debug("ℹ️ 스트림 트랙 종료 중 예외:", err);
    }
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

    // ⛑️ 핵심: 에러에서 즉시 start 금지 → abort로 종료만 하고 재시작은 onend에서.
    this.recognition.onerror = (event) => {
      console.error("🎙️ 음성 인식 에러:", event.error);
      if (
        event.error === "no-speech" ||
        event.error === "network" ||
        event.error === "aborted" ||
        event.error === "audio-capture"
      ) {
        if (this.recognition && typeof this.recognition.abort === "function") {
          try {
            this.recognition.abort();
          } catch (err) {
            console.debug("ℹ️ recognition.abort() 실패:", err);
          }
        }
      }
    };

    // 종료 시점에서만 재시작 담당
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
    if (!this.recognition) {
      this.isRecognizing = false;
      return;
    }

    // onend를 비활성화(수동 종료 시 재연결 방지)
    try {
      this.recognition.onend = null;
    } catch (err) {
      console.debug("ℹ️ recognition.onend null 처리 실패:", err);
    }

    // stop → abort 순서로 종료 시도
    try {
      if (typeof this.recognition.stop === "function") this.recognition.stop();
    } catch (err) {
      console.debug("ℹ️ recognition.stop() 실패:", err);
    }

    try {
      if (typeof this.recognition.abort === "function") this.recognition.abort();
    } catch (err) {
      console.debug("ℹ️ recognition.abort() 실패:", err);
    }

    this.recognition = null;
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
