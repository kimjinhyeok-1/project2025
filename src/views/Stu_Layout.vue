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
      <li class="nav-item my-2">
        <a
          class="nav-link collapsed"
          href="#"
          data-toggle="collapse"
          data-target="#collapseQuestion"
          aria-expanded="false"
          aria-controls="collapseQuestion"
        >
          <i class="fas fa-question-circle"></i>
          <span>질문</span>
        </a>
        <div id="collapseQuestion" class="collapse" data-parent="#studentSidebar">
          <div class="bg-white py-2 collapse-inner rounded text-center">
            <router-link class="collapse-item my-1" to="/student/qna">Q & A</router-link>
            <router-link class="collapse-item my-1" to="/student/history">HISTORY</router-link>
          </div>
        </div>
      </li>

      <!-- ✅ 수업 드롭다운 -->
      <li class="nav-item my-2">
        <a
          class="nav-link collapsed"
          href="#"
          data-toggle="collapse"
          data-target="#collapseLesson"
          aria-expanded="false"
          aria-controls="collapseLesson"
        >
          <i class="fas fa-chalkboard-teacher"></i>
          <span>수업</span>
        </a>
        <div id="collapseLesson" class="collapse" data-parent="#studentSidebar">
          <div class="bg-white py-2 collapse-inner rounded text-center">
            <router-link class="collapse-item my-1" to="/student/summary">REVIEW</router-link>
            <router-link class="collapse-item my-1" to="/student/lessonquestion">Q & A</router-link>
          </div>
        </div>
      </li>

      <!-- 과제 메뉴 -->
      <li class="nav-item my-2">
        <router-link class="nav-link" to="/student/assignment">
          <i class="fas fa-book"></i>
          <span>과제</span>
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
/* ✅ 아이콘 및 텍스트 정렬 + 사이즈 통일 */
.sidebar .nav-link {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  text-align: center !important;
  position: relative;
}

.sidebar .nav-link i {
  font-size: 1.6rem !important;
  margin-bottom: 6px;
  line-height: 1;
  display: block;
  color: rgba(255, 255, 255, 0.8);
}

.sidebar .nav-link span {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

/* ✅ 메뉴 항목 여백 */
.nav-item {
  margin-top: 0.5rem !important;
  margin-bottom: 0.5rem !important;
}

/* ✅ collapse 내부 항목 */
.collapse-inner .collapse-item {
  font-size: 1rem;
  font-weight: 500;
}

/* ✅ 상단 아이콘 색상 */
.sidebar-brand-icon i {
  color: rgba(255, 255, 255, 0.8);
}
</style>
