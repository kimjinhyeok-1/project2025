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
          <span> Q & A</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" to="/professor/lesson">
          <i class="fas fa-chalkboard"></i>
          <span> LECTURE START</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" to="/professor/review">
          <i class="fas fa-book-open"></i>
          <span> LECTURE REVIEW</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" to="/professor/assignments">
          <i class="fas fa-tasks"></i>
          <span> ASSIGNMENT</span>
        </router-link>
      </li>
      <!-- ✅ 새 메뉴 추가 -->
      <li class="nav-item">
        <router-link class="nav-link" to="/professor/realtime-question">
          <i class="fas fa-microphone"></i>
          <span> REALTIME QUESTION</span>
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
