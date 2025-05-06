<template>
  <div class="lecture-container mt-5">
    <h2 class="text-center">🎤 수업 녹화 & 음성 인식</h2>
    <p class="text-muted text-center">
      녹음 중 키워드가 감지되면 자동으로 화면 캡처와 함께 백엔드에 전송됩니다.
    </p>

    <div class="btn-group d-flex justify-content-center mt-4">
      <button class="btn btn-primary m-2" @click="toggleAudioRecording">
        {{ isRecording ? "🔝 음성 인식 종료" : "🎙️ 음성 인식 시작" }}
      </button>

      <button class="btn btn-warning m-2" @click="testOptions">
        🧪 OPTIONS 테스트
      </button>
    </div>

    <div
      v-if="summaryResult"
      class="alert alert-success mt-4 markdown-body"
    >
      <h5>📘 수업 요약 결과:</h5>
      <div v-html="renderedSummary"></div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import recordingManager from "@/managers/RecordingManager";
import { testOptionsRequest } from "@/api/snapshotService";
import { marked } from "marked";

export default {
  name: "ProfessorLesson",
  data() {
    return {
      isRecording: false,
      summaryResult: null,
    };
  },
  computed: {
    renderedSummary() {
      return this.summaryResult ? marked.parse(this.summaryResult) : "";
    },
  },
  methods: {
    async startLectureSession() {
      try {
        const res = await axios.post(
          "https://project2025-backend.onrender.com/snapshots/lectures",
          {}, // ✅ 빈 JSON 바디 명시
          {
            headers: {
              "Content-Type": "application/json" // ✅ 명시적 JSON 타입
            }
          }
        );

        const { lecture_id } = res.data;
        localStorage.setItem("lecture_id", lecture_id);

        // ✅ 녹음 매니저에도 설정
        recordingManager.setLectureId(lecture_id);

        console.log("🎓 수업 세션 시작:", lecture_id);
        return lecture_id;
      } catch (err) {
        console.error("❌ 수업 세션 시작 실패:", err);
        alert("수업 세션 생성에 실패했습니다.");
        return null;
      }
    },

    async toggleAudioRecording() {
      if (!recordingManager.getState().isRecording) {
        const lectureId = await this.startLectureSession();
        if (!lectureId) {
          alert("수업 세션이 생성되지 않아 녹음을 시작할 수 없습니다.");
          return;
        }
        await recordingManager.startRecording();
      } else {
        recordingManager.stopRecording();
        this.isRecording = recordingManager.getState().isRecording;
        await this.requestLectureSummary();
      }
      this.isRecording = recordingManager.getState().isRecording;
    },

    async requestLectureSummary() {
      try {
        const lectureId = localStorage.getItem("lecture_id");
        if (!lectureId) throw new Error("lecture_id가 없습니다. 세션을 먼저 시작하세요.");

        const response = await fetch(
          `https://project2025-backend.onrender.com/snapshots/generate_markdown_summary?lecture_id=${lectureId}`
        );
        if (!response.ok) throw new Error("요약 요청 실패");

        const data = await response.json();
        this.summaryResult = data.summary;
        console.log("📘 요약 결과:", data.summary);
      } catch (error) {
        console.error("❌ 수업 요약 요청 실패:", error);
        alert("요약 요청에 실패했습니다.");
      }
    },

    async testOptions() {
      await testOptionsRequest();
    },
  },
  mounted() {
    this.isRecording = recordingManager.getState().isRecording;

    recordingManager.subscribe((newState) => {
      this.isRecording = newState;
    });

    recordingManager.reconnectRecognition();
  },
};
</script>

<style scoped>
.lecture-container {
  max-width: 900px;
  margin: auto;
  padding: 30px;
}

/* ✅ 마크다운 렌더링 시 왼쪽 정렬 적용 */
.markdown-body {
  text-align: left;
  white-space: normal;
}

/* ✅ 마크다운 스타일 보정 */
.markdown-body h3 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #155724;
  margin-top: 1.5rem;
}

.markdown-body ul {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.markdown-body li {
  margin-bottom: 0.5rem;
}
</style>
