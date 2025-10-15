<template>
  <div class="main-card">
    <h2 class="main-title">📄 수업 복습 상세보기</h2>

    <div v-if="loading" class="text-muted mt-3">요약을 불러오는 중입니다...</div>

    <div v-else-if="summaryData.length">
      <div v-for="(topic, index) in summaryData" :key="index" class="topic-block">
        <!-- 왼쪽 회색 네모 -->
        <div class="topic-summary">
          <h4 class="topic-title">📘 {{ topic.topic }}</h4>
          <p class="topic-text" v-html="formatSummary(topic.summary)"></p>
        </div>

        <!-- 오른쪽 교수님의 한마디 -->
        <div class="professor-note">
          <div class="label">👨‍🏫 교수님의 한마디</div>
          <ul class="script-list">
            <li v-for="(highlight, idx) in topic.highlights" :key="idx" class="script-item">
              <span
                v-if="highlight.image_url && highlight.image_url.trim() !== ''"
                class="script-link"
                @click="openModal(toFullUrl(highlight.image_url))"
              >
                🗣 {{ highlight.text }}
              </span>
              <span v-else>🗣 {{ highlight.text }}</span>
            </li>
          </ul>
        </div>
      </div>

      <button class="btn btn-outline-secondary back-button" @click="$router.back()">
        ← 강의 목록으로 돌아가기
      </button>
    </div>

    <div v-else class="alert alert-warning mt-3">
      📂 아직 생성된 수업 요약이 없거나, 해당 강의에 대한 요약 데이터가 없습니다.
    </div>

    <!-- 이미지 팝업 -->
    <div v-if="modalImageUrl" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-content">
        <img :src="modalImageUrl" alt="확대된 이미지" />
        <button class="close-btn" @click="closeModal">닫기 ✖</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const lectureId = route.params.id;

const summaryData = ref([]);
const loading = ref(true);
const modalImageUrl = ref('');

// ✅ image_url 상대 경로 처리
const toFullUrl = (path) => {
  if (!path) return '';
  return path.startsWith('/static')
    ? `https://project2025-backend.onrender.com${path}`
    : path;
};

// ✅ summary 줄바꿈 처리 함수
const formatSummary = (text) => {
  if (!text) return '';
  return text
    .split('\n')
    .map(line => line.startsWith('- ') ? `<br>${line}` : line)
    .join('')
    .replace(/\n/g, '<br>');
};

const openModal = (url) => {
  modalImageUrl.value = url;
};

const closeModal = () => {
  modalImageUrl.value = '';
};

// ✅ 시간 포맷 함수 (ProfessorLesson.vue와 동일)
const formatElapsed = (ms) => {
  const safe = Math.max(0, Math.round(ms));
  const mm = Math.floor(safe / 60000);
  const ss = Math.floor((safe % 60000) / 1000);
  const cc = Math.floor((safe % 1000) / 10);
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(mm)}.${pad(ss)}.${pad(cc)}초`;
};

// ✅ 리뷰 생성 완료 시간 측정 및 콘솔 출력
const logReviewGenerationTime = () => {
  const startStr = sessionStorage.getItem('review_timing_start');
  if (startStr) {
    const start = Number(startStr);
    const now =
      typeof performance !== 'undefined' && typeof performance.now === 'function'
        ? performance.now()
        : Date.now();

    const elapsed = now - start;
    sessionStorage.removeItem('review_timing_start');

    console.log(`✅ 리뷰 결과 생성 완료: 소요 시간(${formatElapsed(elapsed)})`);
  } else {
    console.warn('⚠️ review_timing_start가 없어 리뷰 생성 시간 측정을 건너뜁니다.');
  }
};

// ✅ 강의 요약 데이터 불러오기
const fetchLectureSummary = async () => {
  try {
    const response = await axios.get(
      `https://project2025-backend.onrender.com/snapshots/lecture_summary?lecture_id=${lectureId}`
    );
    summaryData.value = response.data;
  } catch (error) {
    console.error('❌ 요약 불러오기 실패:', error);
  } finally {
    loading.value = false;
    // 📍 데이터 로드 완료 후 시간 측정 로그 실행
    logReviewGenerationTime();
  }
};

// ✅ 마운트 시 데이터 요청
onMounted(fetchLectureSummary);
</script>

<style scoped>
.main-card {
  max-width: 1000px;
  background: white;
  margin: auto;
  margin-top: 2rem;
  padding: 2rem;
  border-radius: 1.2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.main-title {
  font-size: 1.6rem;
  font-weight: bold;
  margin-bottom: 2rem;
  text-align: center;
}
.topic-block {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  position: relative;
}
.topic-summary {
  background-color: #f5f5f5;
  border-radius: 1rem;
  padding: 1.2rem;
  flex: 1 1 60%;
  margin-right: 1rem;
}
.topic-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 0.8rem;
}
.topic-text {
  color: #333;
  line-height: 1.6;
}
.professor-note {
  flex: 0 0 35%;
  padding: 0.5rem 0.2rem;
}
.label {
  background-color: #3b4890;
  color: white;
  font-weight: bold;
  padding: 0.4rem 0.75rem;
  border-radius: 0.5rem;
  margin-bottom: 0.6rem;
  display: inline-block;
}
.script-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.script-item {
  margin-bottom: 0.5rem;
}
.script-link {
  cursor: pointer;
  text-decoration: underline dotted;
  color: inherit;
}
.script-link:hover {
  text-decoration: underline;
}
.back-button {
  display: block;
  margin: 0 auto;
  margin-top: 1rem;
}
.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}
.modal-content {
  background: white;
  border-radius: 1rem;
  padding: 1rem;
  max-width: 90%;
  max-height: 90%;
  overflow: auto;
  position: relative;
}
.modal-content img {
  max-width: 100%;
  max-height: 80vh;
  display: block;
  margin: auto;
}
.close-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}
</style>
