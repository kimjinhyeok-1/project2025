<template>
  <div id="wrapper" class="d-flex">
    <!-- Sidebar -->
    <ul class="navbar-nav bg-info sidebar sidebar-light accordion" id="studentSidebar">
      <router-link class="sidebar-brand d-flex align-items-center justify-content-center" to="/student">
        <div class="sidebar-brand-icon">
          <i class="fas fa-user-graduate"></i>
        </div>
        <div class="sidebar-brand-text mx-3">STUDENT</div>
      </router-link>

      <hr class="sidebar-divider my-0" />

      <!-- Q&A 메뉴 -->
      <li class="nav-item">
        <router-link class="nav-link" to="/student/qna">
          <i class="fas fa-question-circle"></i>
          <span> Q & A</span>
        </router-link>
      </li>

      <!-- 새로 추가될 메뉴 -->
      <li class="nav-item">
        <router-link class="nav-link" to="/student/summary">
          <i class="fas fa-file-alt"></i>
          <span> 요약 요약!</span>
        </router-link>
      </li>

      <li class="nav-item">
        <router-link class="nav-link" to="/student/lessonquestion">
          <i class="fas fa-lightbulb"></i>
          <span> 강의 중 질문 </span>
        </router-link>
      </li>

      <!-- ✅ 대화 기록 보기 메뉴 (확실히 추가) -->
      <li class="nav-item">
        <router-link class="nav-link" to="/student/history">
          <i class="fas fa-comments"></i>
          <span> 대화 기록 보기</span>
        </router-link>
      </li>

      <!-- 과제 메뉴 -->
      <li class="nav-item">
        <router-link class="nav-link" to="/student/assignment">
           <i class="fas fa-book"></i>
           <span> ASSIGNMENT</span>
        </router-link>
      </li>
    </ul>

    <!-- Main Content -->
    <div id="content-wrapper" class="flex-grow-1">
      <div id="content" class="p-4">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
html, body, #app, #wrapper {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

#wrapper {
  display: flex;
}

.sidebar {
  min-height: 100vh;
  position: sticky;
  top: 0;
  left: 0;
}

.sidebar .nav-link,
.sidebar .sidebar-brand,
.sidebar .nav-link span {
  color: white !important;
}

#content-wrapper {
  flex-grow: 1;
  width: 100%;
  background-color: #f8f9fc;
}

#content {
  width: 100%;
}
</style>

<script setup>
console.log("👀 StudentLayout.vue 진입됨")
</script>

