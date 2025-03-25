<template>
  <div class="text-center d-flex align-items-center justify-content-center mt-5">
    <!-- 로고 GIF -->
    <img src="/kut_logo.gif" alt="Logo" class="logo-gif me-3" />

    <!-- 사이트 이름 -->
    <div>
      <h1 class="mb-1">KOREATECH</h1>
      <p class="text-muted">온라인 교육</p>
    </div>
  </div>
</template>
  
  <script>
  export default {
    name: "HomeView", // Home -> HomeView 변경
  };
  </script>

<style scoped>
.logo-gif {
  width: 60px;
  height: auto;
  margin-right: 15px;
  border-radius: 8px;
}
.mb-1 {
  font-family: 'Do Hyeon', sans-serif;
  font-size: 2.0rem;
  font-weight: 700;
  color: #1a1a1a;
}

.text-muted {
  font-family: 'Do Hyeon', sans-serif;
  font-size: 1.0rem;
  font-weight: 600;
  color: #555;
}
</style>