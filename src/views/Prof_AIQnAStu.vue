<script>
import recordingManager from "@/managers/RecordingManager";

export default {
  data() {
    return {
      recognitionStatus: '수업 중',
      tab: 'recent',
      questions: [],
      latestTranscript: '',
      lastTriggeredText: '',
      transcriptCallback: null
    };
  },
  computed: {
    filteredQuestions() {
      return [...this.questions].sort((a, b) =>
        this.tab === 'popular' ? b.likes - a.likes : new Date(b.created_at) - new Date(a.created_at)
      );
    }
  },
  mounted() {
    this.fetchQuestions();
    this.transcriptCallback = this.handleTranscript;
    recordingManager.subscribeToTranscript(this.transcriptCallback);
  },
  beforeUnmount() {
    if (this.transcriptCallback) {
      recordingManager.unsubscribeFromTranscript(this.transcriptCallback);
    }
  },
  watch: {
    tab() {
      this.fetchQuestions();
    }
  },
  methods: {
    async fetchQuestions() {
      try {
        const url = this.tab === 'recent'
          ? 'https://project2025-backend.onrender.com/vad/questions'
          : 'https://project2025-backend.onrender.com/vad/questions/popular_summary';

        const res = await fetch(url);
        const data = await res.json();

        this.questions = this.tab === 'recent'
          ? data.results
          : data.results.map(q => ({
              text: `${q.text} (${q.unknown_percent}%)`,
              created_at: new Date()
            }));
      } catch (err) {
        console.error('❌ 질문 목록 불러오기 실패:', err);
      }
    },
    async handleTranscript(transcript) {
      this.latestTranscript = transcript;
      console.log("🎙️ 받은 텍스트:", transcript);

      try {
        await fetch("https://project2025-backend.onrender.com/vad/upload_text_chunk", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: transcript })
        });

        if (transcript.includes("질문")) {
          console.log("🧠 '질문' 트리거 감지 → GPT 질문 생성 요청");

          await fetch("https://project2025-backend.onrender.com/vad/trigger_question_generation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
          });

          this.lastTriggeredText = transcript;
          await this.fetchQuestions();
        }
      } catch (err) {
        console.error("❌ 질문 생성 중 오류 발생:", err);
      }
    }
  }
};
</script>
