<template>
  <div class="container mt-5">
    <h2>📄 수업 복습 상세보기</h2>

    <div v-if="loading" class="text-muted mt-3">
      요약을 불러오는 중입니다...
    </div>

    <div v-else-if="summaryData.length">
      <div v-for="(topic, index) in summaryData" :key="index" class="topic-section mb-5">
        <h4>📘 {{ topic.topic }}</h4>
        <p class="mb-2 text-muted">{{ topic.summary }}</p>

        <ul>
          <li v-for="(highlight, idx) in topic.highlights" :key="idx">
            <p
              v-if="highlight.image_url && highlight.image_url.trim() !== ''"
              class="mb-1 clickable-text"
              @click="openModal(highlight.image_url)"
            >
              🗣 {{ highlight.text }}
            </p>
            <p v-else class="mb-1">
              🗣 {{ highlight.text }}
            </p>
          </li>
        </ul>
      </div>

      <button class="btn btn-outline-secondary" @click="$router.back()">← 목록으로 돌아가기</button>
    </div>

    <div v-else class="alert alert-warning mt-3">
      📂 수업 요약이 아직 생성되지 않았거나, 해당 lecture_id에 대한 요약 파일이 존재하지 않습니다.
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
.container {
  background-color: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
  max-width: 900px;
  margin: auto;
}
.topic-section {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 1rem;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.05);
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-content {
  position: relative;
  background: white;
  padding: 1rem;
  border-radius: 1rem;
  max-width: 90%;
  max-height: 90%;
  overflow: auto;
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
.clickable-text {
  cursor: pointer;
  text-decoration: underline dotted;
  color: inherit;
}
.clickable-text:hover {
  text-decoration: underline;
}
</style>
