<template>
    <div class="container mt-5">
      <h2>📄 수업 복습 상세보기</h2>
  
      <div v-if="loading" class="text-muted mt-3">요약을 불러오는 중입니다...</div>
  
      <div v-else-if="summaryData.length">
        <div
          v-for="(topic, index) in summaryData"
          :key="index"
          class="topic-section mb-5"
        >
          <h4>📘 {{ topic.topic }}</h4>
          <p class="mb-2 text-muted">{{ topic.summary }}</p>
  
          <ul>
            <li v-for="(highlight, idx) in topic.highlights" :key="idx">
              <p class="mb-1">🗣 {{ highlight.text }}</p>
              <img
                v-if="highlight.image_url"
                :src="highlight.image_url"
                alt="스크린샷"
                class="screenshot-preview"
              />
            </li>
          </ul>
        </div>
  
        <button class="btn btn-outline-secondary" @click="$router.back()">
          ← 목록으로 돌아가기
        </button>
      </div>
  
      <div v-else class="alert alert-warning mt-3">
        ❗ 요약 정보를 불러올 수 없습니다.
      </div>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref } from "vue";
  import axios from "axios";
  
  const summaryData = ref([]);
  const loading = ref(true);
  
  const fetchLectureSummary = async () => {
    try {
      const response = await axios.get(
        "https://project2025-backend.onrender.com/lecture_summary?lecture_id=1"
      );
      summaryData.value = response.data;
      console.log("📘 최종 요약 데이터:", summaryData.value);
    } catch (error) {
      console.error("❌ 최종 요약 불러오기 실패:", error);
    } finally {
      loading.value = false;
    }
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
  .screenshot-preview {
    max-width: 100%;
    height: auto;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
  }
  </style>
  