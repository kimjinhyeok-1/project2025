<template>
  <div class="qna-wrapper">
    <h2 class="title">🎤 실시간 질문 생성 (교수용)</h2>
    <p class="text-muted">"질문"이라는 단어가 감지되면 누적 내용을 기반으로 GPT 질문이 생성됩니다.</p>

    <div class="control-buttons">
      <button class="start-btn" @click="startRecognition">🎙️ 수업 시작</button>
      <button class="stop-btn" @click="stopRecognition">🛑 수업 종료</button>
      <span class="status">현재 상태: <strong>{{ recognitionStatus }}</strong></span>
    </div>

    <div class="log-box mt-3">
      <p><strong>🎧 최근 인식된 문장:</strong> {{ latestTranscript }}</p>
      <p v-if="lastTriggeredText"><strong>🧠 최근 질문 트리거:</strong> "{{ lastTriggeredText }}"</p>
    </div>

    <div class="tab-group">
      <button :class="{ active: tab === 'recent' }" @click="tab = 'recent'">Recent</button>
      <button :class="{ active: tab === 'popular' }" @click="tab = 'popular'">Popular</button>
    </div>

    <div v-if="questions.length" class="question-list">
      <div v-for="q in filteredQuestions" :key="q.id" class="question-item">
        <p class="question-text">{{ q.text }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import recordingManager from "@/managers/RecordingManager";
import { generateQuestionsFromParagraph } from "@/api/aiQnaService";

export default {
  name: "ProfAIQnAStu",
  data() {
    return {
      recognitionStatus: "대기 중",
      latestTranscript: "",
      lastTriggeredText: "",
      questions: [],
      tab: "recent",
    };
  },
  computed: {
    filteredQuestions() {
      return this.tab === "recent"
        ? this.questions.slice().reverse()
        : this.questions.filter((q) => q.popular);
    },
  },
  methods: {
    startRecognition() {
      recordingManager.setMode("segment");
      recordingManager.startRecording();
      recordingManager.onSegment(this.handleSegment);
      this.recognitionStatus = "인식 중";
    },
    stopRecognition() {
      recordingManager.stopRecording();
      this.recognitionStatus = "대기 중";
    },
    async handleSegment(paragraph) {
      this.latestTranscript = paragraph;
      if (paragraph.includes("질문")) {
        this.lastTriggeredText = paragraph;
        try {
          const result = await generateQuestionsFromParagraph(paragraph);
          this.questions.push(...result);
        } catch (error) {
          console.error("❌ 질문 생성 실패:", error);
        }
      }
    },
  },
};
</script>

<style scoped>
/* 기존 스타일 유지 */
</style>
