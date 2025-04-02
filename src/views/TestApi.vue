<!-- src/views/TestApi.vue -->
<template>
    <div>
      ✅ API 연결 확인 중... (F12 → 콘솔에서 결과 확인!)
    </div>
  </template>
  
  <script>
  import api from "@/api";
  
  export default {
    name: "TestApi",
    mounted() {
      api.get("/health")
        .then(res => {
          console.log("✅ 연결 성공:", res.data);
        })
        .catch(err => {
          console.error("❌ 연결 실패:", err);
        });
    }
  };
  </script>
  
  <style scoped>
  div {
    padding: 2rem;
    font-size: 1.2rem;
    color: #444;
  }
  </style>
  