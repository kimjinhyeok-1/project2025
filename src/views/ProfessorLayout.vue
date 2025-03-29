<template>
  <div class="dashboard-container">
    <aside class="sidebar">
      <router-link to="/professor/qna" class="sidebar-btn">질문 & 답변</router-link>
      <router-link to="/professor/lesson" class="sidebar-btn">수업하기</router-link>
      <router-link to="/professor/review" class="sidebar-btn">수업 복습하기</router-link>
      <router-link to="/professor/assignments" class="sidebar-btn">과제 확인</router-link>
    </aside>

    <section class="main-content">
      <router-view />
    </section>
  </div>
</template>

<style scoped>
/* 전체 화면에서 네비게이션 바 아래부터 시작 */
.dashboard-container {
  display: flex;
  height: 100vh;
  margin: 0;
  padding: 0;
}

.sidebar {
  width: 250px; /* 🔹 더 넓게 */
  background-color: #e3f2fd;
  padding: 20px;
  margin: 0;
  border-right: 1px solid #ccc;
  position: fixed;
  top: 56px;
  left: 0;
  bottom: 0;
  box-sizing: border-box;
}

.sidebar-btn {
  display: block;
  width: 100%;
  margin-bottom: 12px;
  padding: 10px 15px;
  background-color: white;
  border: 1px solid #0d6efd; /* 🔹 테두리 얇게 */
  border-radius: 10px;
  color: #0d6efd;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s;
}

.sidebar-btn:hover {
  background-color: #e0edff;
}

.sidebar-btn.router-link-active {
  background-color: #0d6efd;
  color: white;
}

.main-content {
  flex: 1;
  margin-left: 250px; /* 🔹 사이드바 너비만큼 밀어줌 */
  padding: 20px;
  overflow-y: auto;
}
</style>
