<template>
  <div class="page-container">
    <h2 class="page-title">📄 수업 복습 상세보기</h2>

    <div v-if="loading" class="text-muted mt-3">요약을 불러오는 중입니다...</div>

    <div v-else-if="summaryData.length">
      <div v-for="(topic, index) in summaryData" :key="index" class="card">
        <!-- 왼쪽 -->
        <div class="card-left">
          <h4 class="card-topic">📘 {{ topic.topic }}</h4>
          <p class="card-summary">{{ topic.summary }}</p>
        </div>

        <!-- 오른쪽 -->
        <div class="card-right">
          <div class="label">👨‍🏫 교수님의 한마디</div>
          <ul class="script-list">
            <li v-for="(highlight, idx) in topic.highlights" :key="idx" class="script-item">
              <span
                v-if="highlight.image_url && highlight.image_url.trim() !== ''"
                class="script-link"
                @click="openModal(highlight.image_url)"
              >
                🗣 {{ highlight.text }}
              </span>
              <span v-else>🗣 {{ highlight.text }}</span>
            </li>
          </ul>
        </div>
      </div>

      <button class="btn btn-outline-secondary back-button" @click="$router.back()">
        ← 목록으로 돌아가기
      </button>
    </div>

    <div v-else class="alert alert-warning mt-3">
      📂 아직 생성된 수업 요약이 없거나, 해당 강의에 대한 요약 데이터가 없습니다.
    </div>

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
  }
};

const openModal = (url) => {
  modalImageUrl.value = url;
};

const closeModal = () => {
  modalImageUrl.value = '';
};

onMounted(fetchLectureSummary);
</script>

<style scoped>
.page-container {
  max-width: 1000px;
  margin: auto;
  padding: 2rem 1rem;
}
.page-title {
  font-weight: bold;
  font-size: 1.6rem;
  margin-bottom: 2rem;
  text-align: center;
}
.card {
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  gap: 2rem;
}
.card-left {
  width: 60%;
}
.card-topic {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 0.8rem;
}
.card-summary {
  color: #555;
}
.card-right {
  width: 35%;
}
.label {
  background-color: #3b4890;
  color: white;
  font-weight: bold;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
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
