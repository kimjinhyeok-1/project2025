<template>
  <div id="wrapper" class="d-flex">
    <!-- Sidebar -->
    <ul class="navbar-nav bg-gradient-primary sidebar sidebar-dark accordion" id="accordionSidebar">
      <router-link class="sidebar-brand d-flex align-items-center justify-content-center" to="/professor">
        <div class="sidebar-brand-icon">
          <i class="fas fa-chalkboard-teacher"></i>
        </div>
        <div class="sidebar-brand-text mx-3">PROFESSOR</div>
      </router-link>

      <hr class="sidebar-divider my-0" />

      <li class="nav-item">
        <router-link class="nav-link" to="/professor/qna">
          <i class="fas fa-question-circle"></i>
          <span> 학생들의 질문</span>
        </router-link>
      </li>

      <!-- ✅ 드롭다운 메뉴 시작 -->
      <li class="nav-item">
        <a
          class="nav-link collapsed"
          href="#"
          data-toggle="collapse"
          data-target="#collapseLesson"
          aria-expanded="false"
          aria-controls="collapseLesson"
        >
          <i class="fas fa-chalkboard"></i>
          <span> 수업</span>
        </a>
        <div id="collapseLesson" class="collapse" data-parent="#accordionSidebar">
          <div class="bg-white py-2 collapse-inner rounded">
            <router-link class="collapse-item" to="/professor/lesson">수업 시작</router-link>
            <router-link class="collapse-item" to="/professor/review">수업 요약</router-link>
          </div>
        </div>
      </li>
      <!-- ✅ 드롭다운 끝 -->

      <li class="nav-item">
        <router-link class="nav-link" to="/professor/assignments">
          <i class="fas fa-tasks"></i>
          <span> 과제</span>
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
.sidebar .nav-link span {
  font-size: 1.2rem;
  font-weight: 600;
}
</style>