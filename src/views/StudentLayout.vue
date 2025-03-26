<template>
    <div class="dashboard-container">
      <!-- 왼쪽 사이드바 깃허브 연결 완료 -->
      <aside class="sidebar">
        <router-link to="/student/qna" class="sidebar-btn">QnA</router-link>
        <router-link to="/student/assignment" class="sidebar-btn">과제</router-link>
      </aside>
  
      <!-- 오른쪽 메인 콘텐츠 -->
      <section class="main-content">
        <router-view />
      </section>
    </div>
  </template>
  
  <script setup>
  // 여긴 setup 문법 사용 중이므로 별도 로직은 없음
  </script>
  
  <style scoped>
  .dashboard-container {
    display: flex;
    height: 100vh;
    margin: 0;
    padding: 0;
  }
  
  /* 왼쪽 사이드바 스타일 */
  .sidebar {
    width: 250px;
    background-color: #e3f2fd; /* 연한 하늘색 */
    padding: 20px;
    margin: 0;
    border-right: 1px solid #ccc;
    position: fixed;
    top: 56px; /* 상단 네비게이션 바 높이 고려 */
    left: 0;
    bottom: 0;
    box-sizing: border-box;
  }
  
  /* 버튼 (router-link) 스타일 */
  .sidebar-btn {
    display: block;
    width: 100%;
    margin-bottom: 12px;
    padding: 10px 15px;
    background-color: white;
    border: 1px solid #0d6efd;
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
    background-color: #0d6efd; /* 상단바와 동일한 파랑 */
    color: white;
  }
  
  /* 메인 콘텐츠 영역 */
  .main-content {
    flex: 1;
    margin-left: 250px; /* 사이드바 만큼 밀어줌 */
    padding: 20px;
    overflow-y: auto;
  }
  </style>
  