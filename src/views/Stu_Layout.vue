<template>
  <div id="wrapper" class="d-flex">
    <!-- Sidebar -->
    <ul class="navbar-nav sidebar sidebar-light accordion" id="studentSidebar" style="background-color: rgb(43, 132, 183);">
      <router-link class="sidebar-brand d-flex align-items-center justify-content-center" to="/student">
        <div class="sidebar-brand-icon">
          <i class="fas fa-user-graduate"></i>
        </div>
        <div class="sidebar-brand-text mx-3" style="color: rgba(255,255,255,0.9);">STUDENT</div>
      </router-link>

      <hr class="sidebar-divider my-0" />

      <!-- ✅ 질문 드롭다운 -->
      <li class="nav-item">
        <a
          class="nav-link collapsed"
          href="#"
          data-toggle="collapse"
          data-target="#collapseQuestion"
          aria-expanded="false"
          aria-controls="collapseQuestion"
        >
          <i class="fas fa-question-circle"></i>
          <span> 질문 </span>
        </a>
        <div id="collapseQuestion" class="collapse" data-parent="#studentSidebar">
          <div class="bg-white py-2 collapse-inner rounded">
            <router-link class="collapse-item" to="/student/qna">Q & A</router-link>
            <router-link class="collapse-item" to="/student/history">HISTORY</router-link>
          </div>
        </div>
      </li>

      <!-- ✅ 수업 드롭다운 -->
      <li class="nav-item">
        <a
          class="nav-link collapsed"
          href="#"
          data-toggle="collapse"
          data-target="#collapseLesson"
          aria-expanded="false"
          aria-controls="collapseLesson"
        >
          <i class="fas fa-chalkboard-teacher"></i>
          <span> 수업 </span>
        </a>
        <div id="collapseLesson" class="collapse" data-parent="#studentSidebar">
          <div class="bg-white py-2 collapse-inner rounded">
            <router-link class="collapse-item" to="/student/summary">REVIEW</router-link>
            <router-link class="collapse-item" to="/student/lessonquestion">Q & A</router-link>
          </div>
        </div>
      </li>

      <!-- 과제 메뉴 -->
      <li class="nav-item">
        <router-link class="nav-link" to="/student/assignment">
          <i class="fas fa-book"></i>
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
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.2rem;
  font-weight: 600;
}
.sidebar-brand-icon i {
  color: rgba(255, 255, 255, 0.8); /* 부드러운 흰색 */
}

</style>
